import os
import asyncio
from flask import Flask, request, send_from_directory
from aiogram import Bot, Dispatcher, types

# Импортируем bot и dp из существующего модуля
from bot.bot import bot, dp

# Настройки Webhook
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')  # например, https://<your_ngrok_url>
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Создаем Flask приложение
app = Flask(__name__, static_folder='web', static_url_path='')

# Отдаем статику (мини-приложение)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    if path and os.path.exists(os.path.join('web', path)):
        return send_from_directory('web', path)
    # По умолчанию покажем signal.html
    return send_from_directory('web', 'signal.html')

# Точка входа для Telegram Webhook
@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook_handler():
    update = types.Update(**request.get_json())
    # Обрабатываем асинхронно
    asyncio.create_task(dp.process_update(update))
    return "", 200

# Функции установки и удаления webhook
async def on_startup():
    # Устанавливаем webhook в Telegram
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown():
    # Удаляем webhook
    await bot.delete_webhook()

if __name__ == '__main__':
    assert WEBHOOK_HOST, "Укажите переменную окружения WEBHOOK_HOST, например https://abcdef.ngrok-free.app"
    loop = asyncio.get_event_loop()
    loop.run_until_complete(on_startup())
    # Запускаем Flask
    port = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
    # На завершении
    loop.run_until_complete(on_shutdown()) 