from telegram import Bot
from flask import Flask, request, jsonify, send_from_directory
import hashlib
import sqlite3
import os
from dotenv import load_dotenv  # Импортируем load_dotenv
import time
import hashlib
import asyncio
import requests

app = Flask(__name__)

# Загружаем переменные из .env файла
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# === Конфигурация ===
BOT_TOKEN = os.environ.get("BOT_TOKEN")
PROVIDER_TOKEN = os.environ.get("PROVIDER_TOKEN")
DATABASE_FILE = os.path.join(os.path.dirname(__file__), "plinko.db")  # Файл базы данных SQLite

# Проверяем наличие необходимых переменных окружения
if not BOT_TOKEN: # or not PROVIDER_TOKEN:
    print("ERROR: Missing environment variables! Please set BOT_TOKEN in .env file.")
    exit()

# === Подключение к базе данных ===
def get_db_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)  # Подключаемся к файлу
        conn.row_factory = sqlite3.Row #  Чтобы обращаться к колонкам по имени
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# === Создание таблиц (если их нет) ===
def create_tables():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT,
                pp_balance INTEGER DEFAULT 0,
                lang TEXT
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id TEXT PRIMARY KEY,
                telegram_id INTEGER,
                stars_amount INTEGER,
                pp_amount INTEGER,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                invoice_payload TEXT,
                FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id TEXT,
                amount INTEGER,
                status TEXT,
                FOREIGN KEY (invoice_id) REFERENCES invoices(id)
            )
            """)
            conn.commit()
            print("Tables created (if they didn't exist).")

        except Exception as e:
             print(f"Error creating tables: {e}")
        finally:
            cursor.close()
            conn.close()

# === Функции generate_invoice_slug и verify_signature - как в предыдущем примере ===
def generate_invoice_slug(user_id, item_id, amount):
    timestamp = str(int(time.time() * 1000))  # Текущее время в миллисекундах
    data = f"{user_id}-{item_id}-{amount}-{timestamp}-{BOT_TOKEN}"
    return hashlib.sha256(data.encode()).hexdigest()

def verify_signature(data, secret_key, hash_value):
    """Проверяет подпись (хеш) от Telegram для защиты от подделки."""
    data_check_string = "\n".join(
        [f"{key}={data[key]}" for key in sorted(data) if key != "hash"]
    )
    secret_key_encoded = secret_key.encode("utf-8")
    data_check_string_encoded = data_check_string.encode("utf-8")
    hmac = hashlib.sha256(secret_key_encoded)
    hmac.update(data_check_string_encoded)
    expected_hash = hmac.hexdigest()
    return expected_hash == hash_value

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text})
    except Exception as e:
        print(f"Error sending message: {e}")

@app.route('/create_invoice', methods=['POST'])
@app.route('/api/create_invoice', methods=['POST'])
async def create_invoice():
    data = request.get_json()
    user_id = data['user_id']
    amount = data['amount'] # Сумма в Stars
    pp_amount = data['pp_amount'] # Сумма PPs, которую получит пользователь
    item_id = "plinko_points"

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # === Добавляем проверку существования пользователя и создание, если его нет ===
            cursor.execute("SELECT telegram_id FROM users WHERE telegram_id = ?", (user_id,))
            user_exists = cursor.fetchone()

            if not user_exists:
                # Создаем пользователя, если его нет
                cursor.execute("INSERT INTO users (telegram_id, username) VALUES (?, ?)", (user_id, "unknown")) # username пока не знаем
                print(f"Created new user with telegram_id: {user_id}")
                conn.commit()

            # ===  Генерируем invoice_payload (это просто пример, в реальном приложении нужно делать что-то более безопасное) ===
            invoice_payload = f"user_id={user_id}&amount={amount}&pp_amount={pp_amount}&item_id={item_id}"
            
            # === Создаем счет ===
            invoice_slug = generate_invoice_slug(user_id, item_id, amount)
            cursor.execute("INSERT INTO invoices (id, telegram_id, stars_amount, pp_amount, status, invoice_payload) VALUES (?, ?, ?, ?, ?, ?)", (invoice_slug, user_id, amount, pp_amount, "pending", invoice_payload))
            conn.commit()
            print(f"Invoice created: {invoice_slug} for user {user_id}")

            # === Создание ссылки на оплату через Telegram Bot API ===
            bot = Bot(BOT_TOKEN) # Создаем экземпляр бота
            try:
                invoice_link = await bot.create_invoice_link( # await
                    title="Plinko Points Purchase",
                    description=f"Purchase of {pp_amount} Plinko Points for {amount} Stars",
                    payload=invoice_payload,  # Важно передавать invoice_payload
                    provider_token="",  # Оставляем пустым для Telegram Stars
                    currency="XTR",
                    prices=[{"label": "Plinko Points", "amount": amount}] # Убрали умножение на 100, так как Stars не имеют копеек
                )
                print(f"Telegram API Invoice Link created for user {user_id}")
                return jsonify({'invoiceLink': invoice_link, 'error': None})  # Возвращаем invoiceLink и error: null
            except Exception as e:
                print(f"Error creating invoice link via Telegram API: {e}")
                return jsonify({'invoiceLink': None, 'error': str(e)}), 500 # Возвращаем invoiceLink: null и сообщение об ошибке


        except Exception as e:
            print(f"Error creating invoice in database: {e}")
            return jsonify({'invoiceLink': None, 'error': 'Failed to create invoice'}), 500 # Возвращаем invoiceLink: null и сообщение об ошибке
        finally:
            cursor.close()
            conn.close()


@app.route('/payment_callback', methods=['POST'])
def payment_callback():
    data = request.form # Или request.get_json(), в зависимости от формата данных

    # === ВАЖНО: ПРОВЕРКА ПОДПИСИ (ХЕША) ОТ TELEGRAM ===
    secret_key = hashlib.sha256(PROVIDER_TOKEN.encode('utf-8')).hexdigest()
    is_valid = verify_signature(data, secret_key, data.get('hash', ''))

    if not is_valid:
        print("WARNING: INVALID SIGNATURE FROM TELEGRAM! Possible spoofing attempt.")
        return jsonify({'ok': False, 'error': 'Invalid signature'}), 400

    invoice_payload = data.get('invoice_payload') # Получаем invoice_payload (может быть пустым!)
    print(f"Payment callback received for invoice (payload): {invoice_payload}")

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            #  Ищем счет в базе данных по invoice_payload (или по invoice_slug, если используешь его)
            cursor.execute("SELECT telegram_id, pp_amount FROM invoices WHERE invoice_payload = ?", (invoice_payload,))
            result = cursor.fetchone()

            if result:
                telegram_id, pp_amount = result['telegram_id'], result['pp_amount']
                if data.get('payment_status') == 'paid': # Или другой статус успеха

                    # === Обновляем баланс пользователя ===
                    cursor.execute("UPDATE users SET pp_balance = pp_balance + ? WHERE telegram_id = ?", (pp_amount, telegram_id))

                    # === Обновляем статус счета ===
                    cursor.execute("UPDATE invoices SET status = 'paid' WHERE invoice_payload = ?", (invoice_payload,))
                    conn.commit()
                    print(f"Payment processed successfully for user {telegram_id}, added {pp_amount} PPs.")
                    return jsonify({'ok': True})
                else:
                    print(f"Payment failed for invoice (payload) {invoice_payload}")
                    cursor.execute("UPDATE invoices SET status = 'failed' WHERE invoice_payload = ?", (invoice_payload,))
                    conn.commit()
                    return jsonify({'ok': False, 'error': 'Payment failed'}), 400
            else:
                print(f"Invoice not found with payload (or id): {invoice_payload}")
                return jsonify({'ok': False, 'error': 'Invoice not found'}), 404
        except Exception as e:
            print(f"Error processing payment callback: {e}")
            return jsonify({'ok': False, 'error': 'Internal server error'}), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({'error': 'Database connection failed'}), 500


@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    update = request.get_json()
    print('Received webhook update:', update)

    # === Обработка команд пользователя ===
    if 'message' in update:
        message = update['message']
        chat_id = message['chat']['id']
        text = message.get('text', '')
        if text == '/start':
            send_message(chat_id, "Добро пожаловать в Plinko!\nИспользуйте /balance чтобы узнать свой баланс.")
        elif text == '/help':
            send_message(chat_id, "Доступные команды:\n/start — запуск бота\n/balance — узнать баланс\n/help — помощь")
        elif text == '/balance':
            telegram_id = message['from']['id']
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("SELECT pp_balance FROM users WHERE telegram_id = ?", (telegram_id,))
                    result = cursor.fetchone()
                    if result:
                        balance = result['pp_balance']
                        send_message(chat_id, f"Ваш баланс: {balance} PPs")
                    else:
                        send_message(chat_id, "Пользователь не найден. Попробуйте совершить первую покупку через мини-приложение.")
                except Exception as e:
                    print(f"Error fetching balance: {e}")
                    send_message(chat_id, "Ошибка при получении баланса.")
                finally:
                    cursor.close()
                    conn.close()
            else:
                send_message(chat_id, "Ошибка подключения к базе данных.")

    # === Обработка успешного платежа ===
    message = update.get('message')
    if message and 'successful_payment' in message:
        successful_payment = message['successful_payment']
        telegram_id = message['from']['id']
        payload = successful_payment.get('invoice_payload')
        total_amount = successful_payment.get('total_amount')
        currency = successful_payment.get('currency')
        print(f"Successful payment from {telegram_id}: {total_amount} {currency}, payload: {payload}")

        # Найти счет по payload и обновить баланс
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT pp_amount FROM invoices WHERE invoice_payload = ?", (payload,))
                result = cursor.fetchone()
                if result:
                    pp_amount = result['pp_amount']
                    cursor.execute("UPDATE users SET pp_balance = pp_balance + ? WHERE telegram_id = ?", (pp_amount, telegram_id))
                    cursor.execute("UPDATE invoices SET status = 'paid' WHERE invoice_payload = ?", (payload,))
                    conn.commit()
                    print(f"Balance updated for user {telegram_id}, added {pp_amount} PPs.")
                    send_message(telegram_id, f"Платёж успешно завершён! На ваш баланс зачислено {pp_amount} PPs.")
                else:
                    print(f"Invoice not found for payload: {payload}")
            except Exception as e:
                print(f"Error updating balance on webhook: {e}")
            finally:
                cursor.close()
                conn.close()
        return jsonify({'ok': True})
    return jsonify({'ok': True})


def ensure_user_exists(telegram_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (telegram_id, username, pp_balance, lang) VALUES (?, ?, ?, ?)", (telegram_id, "unknown", 0, "en"))
        conn.commit()
        cursor.close()
        conn.close()

@app.route('/api/get_balance', methods=['GET'])
def get_balance():
    telegram_id = request.args.get('telegram_id')
    if not telegram_id:
        return jsonify({'ok': False, 'error': 'telegram_id is required'}), 400
    ensure_user_exists(telegram_id)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT pp_balance FROM users WHERE telegram_id = ?", (telegram_id,))
            result = cursor.fetchone()
            if result:
                return jsonify({'ok': True, 'pp_balance': result['pp_balance']})
            else:
                return jsonify({'ok': False, 'error': 'User not found'}), 404
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({'ok': False, 'error': 'DB connection error'}), 500


@app.route('/api/update_balance', methods=['POST'])
def update_balance():
    data = request.get_json()
    telegram_id = data.get('telegram_id')
    delta = data.get('delta')  # может быть отрицательным (уменьшение) или положительным (увеличение)
    if telegram_id is None or delta is None:
        return jsonify({'ok': False, 'error': 'telegram_id and delta are required'}), 400
    ensure_user_exists(telegram_id)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET pp_balance = pp_balance + ? WHERE telegram_id = ?", (delta, telegram_id))
            conn.commit()
            cursor.execute("SELECT pp_balance FROM users WHERE telegram_id = ?", (telegram_id,))
            result = cursor.fetchone()
            if result:
                return jsonify({'ok': True, 'pp_balance': result['pp_balance']})
            else:
                return jsonify({'ok': False, 'error': 'User not found'}), 404
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({'ok': False, 'error': 'DB connection error'}), 500


# === Отдача статики фронтенда (Vite build) ===
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    # Не перехватываем API и webhook только для GET-запросов
    if request.method == 'GET' and (
        path.startswith('api') or
        path.startswith('webhook') or
        path.startswith('payment_callback') or
        path.startswith('create_invoice')
    ):
        return "Not Found", 404
    dist_dir = os.path.join(os.path.dirname(__file__), 'dist')
    if path != "" and os.path.exists(os.path.join(dist_dir, path)):
        return send_from_directory(dist_dir, path)
    else:
        return send_from_directory(dist_dir, 'index.html')


if __name__ == '__main__':
    create_tables()  # Создаем таблицы при запуске приложения (если их нет)
    try:
        app.run(host="0.0.0.0", port=3001, debug=True)
    except OSError as e:
        print(f"[ERROR] Не удалось запустить Flask на порту 3001: {e}\nПроверь, что порт 3001 свободен или освободи его командой 'lsof -i :3001' и 'kill <PID>'")