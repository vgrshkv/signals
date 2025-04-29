import os
import asyncio
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
import aiosqlite

BOT_TOKEN = "8187917166:AAHWD0Zue4961kwQqQmAoA5VQtsJojloSNA"
DATABASE_FILE = os.path.abspath("plinko.db")
MINI_APP_URL = "https://t.me/plinostar_bot/PLINAPP"  # Замените на вашу ссылку

LANGS = {
    'en': {'flag': '🇬🇧', 'name': 'English'},
    'ru': {'flag': '🇷🇺', 'name': 'Русский'},
    'es': {'flag': '🇪🇸', 'name': 'Español'},
    'pt': {'flag': '🇵🇹', 'name': 'Português'},
    'hi': {'flag': '🇮🇳', 'name': 'हिन्दी'},
}

MESSAGES = {
    'welcomeImageCaption': {
        'en': "Welcome to Plinko!",
        'ru': "Добро пожаловать в Plinko!",
        'es': "¡Bienvenido a Plinko!",
        'pt': "Bem-vindo ao Plinko!",
        'hi': "Plinko में आपका स्वागत है!",
    },
    'chooseAction': {
        'en': "Choose an action:",
        'ru': "Выберите действие:",
        'es': "Elige una acción:",
        'pt': "Escolha uma ação:",
        'hi': "कोई क्रिया चुनें:",
    },
    'welcome': {
        'en': "Welcome to Plinko!\n\nChoose an action:",
        'ru': "Добро пожаловать в Plinko!\n\nВыберите действие:",
        'es': "¡Bienvenido a Plinko!\n\nElige una acción:",
        'pt': "Bem-vindo ao Plinko!\n\nEscolha uma ação:",
        'hi': "Plinko में आपका स्वागत है!\n\nकोई क्रिया चुनें:",
    },
    'topup': {
        'en': "Choose the amount to top up:",
        'ru': "Выберите сумму для пополнения:",
        'es': "Elige la cantidad para recargar:",
        'pt': "Escolha o valor para recarregar:",
        'hi': "रिचार्ज के लिए राशि चुनें:",
    },
    'language': {
        'en': "Choose your language:",
        'ru': "Выберите язык:",
        'es': "Elige tu idioma:",
        'pt': "Escolha seu idioma:",
        'hi': "अपनी भाषा चुनें:",
    },
    'lang_updated': {
        'en': "Language updated!",
        'ru': "Язык обновлён!",
        'es': "Idioma actualizado!",
        'pt': "Idioma atualizado!",
        'hi': "भाषा अपडेट की गई!",
    },
}

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

async def get_user_lang(user_id):
    async with aiosqlite.connect(DATABASE_FILE) as db:
        async with db.execute("SELECT lang FROM users WHERE telegram_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row and row[0] else 'en'

def main_menu(lang='en'):
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="🎮 " + ("Play" if lang == 'en' else "Играть" if lang == 'ru' else "Jugar" if lang == 'es' else "Jogar" if lang == 'pt' else "खेलें"), url=MINI_APP_URL)],
            [types.InlineKeyboardButton(text="💰 " + ("Top up" if lang == 'en' else "Пополнить" if lang == 'ru' else "Recargar" if lang == 'es' else "Recarregar" if lang == 'pt' else "रिचार्ज"), callback_data="topup_menu")],
            [types.InlineKeyboardButton(text=f"🌐 Language {LANGS[lang]['flag']}", callback_data="lang_menu")]
        ]
    )

def topup_menu(lang='en'):
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=f"100 PPs (100 Stars)", callback_data="buy_100")],
            [types.InlineKeyboardButton(text=f"500 PPs (500 Stars)", callback_data="buy_500")],
            [types.InlineKeyboardButton(text=f"1000 PPs (1000 Stars)", callback_data="buy_1000")],
            [types.InlineKeyboardButton(text="⬅️ " + ("Back" if lang == 'en' else "Назад" if lang == 'ru' else "Atrás" if lang == 'es' else "Voltar" if lang == 'pt' else "वापस"), callback_data="back_main")]
        ]
    )

def lang_menu():
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=f"{LANGS[code]['flag']} {LANGS[code]['name']}", callback_data=f"setlang_{code}")]
            for code in LANGS
        ] + [[types.InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")]]
    )

@router.message(Command("start"))
async def start_menu(message: types.Message):
    user_id = message.from_user.id
    args = message.get_args() if hasattr(message, 'get_args') else ''
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute("INSERT OR IGNORE INTO users (telegram_id, username, lang) VALUES (?, ?, ?)", (user_id, message.from_user.username or "unknown", 'en'))
        await db.commit()
    lang = await get_user_lang(user_id)
    if args == "topup":
        await message.answer(
            MESSAGES['topup'][lang],
            reply_markup=topup_menu(lang)
        )
    else:
        await message.answer_photo(
            types.FSInputFile(os.path.join("images", "welcome.png")),
            caption=MESSAGES['welcomeImageCaption'][lang]
        )
        await message.answer(
            MESSAGES['chooseAction'][lang],
            reply_markup=main_menu(lang)
        )

@router.callback_query(lambda c: c.data == "topup_menu")
async def show_topup_menu(callback: types.CallbackQuery):
    lang = await get_user_lang(callback.from_user.id)
    await callback.message.edit_text(
        MESSAGES['topup'][lang],
        reply_markup=topup_menu(lang)
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "back_main")
async def back_to_main(callback: types.CallbackQuery):
    lang = await get_user_lang(callback.from_user.id)
    await callback.message.edit_text(
        MESSAGES['welcome'][lang],
        reply_markup=main_menu(lang)
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "lang_menu")
async def show_lang_menu(callback: types.CallbackQuery):
    lang = await get_user_lang(callback.from_user.id)
    await callback.message.edit_text(
        MESSAGES['language'][lang],
        reply_markup=lang_menu()
    )
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("setlang_"))
async def set_language(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    user_id = callback.from_user.id
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute("UPDATE users SET lang = ? WHERE telegram_id = ?", (lang, user_id))
        await db.commit()
    await callback.message.edit_text(
        MESSAGES['welcome'][lang],
        reply_markup=main_menu(lang)
    )
    await callback.answer(MESSAGES['lang_updated'][lang])

@router.callback_query(lambda c: c.data.startswith("buy_"))
async def process_buy(callback_query: types.CallbackQuery):
    amount = int(callback_query.data.split('_')[1])
    prices = [types.LabeledPrice(label=f"{amount} PPs", amount=amount)]
    await bot.send_invoice(
        callback_query.from_user.id,
        title="Покупка Plinko Points",
        description=f"Покупка {amount} Plinko Points",
        provider_token="",  # Для Stars — пустая строка!
        currency="XTR",
        prices=prices,
        payload=f"buy_{amount}"
    )
    await callback_query.answer()

@router.pre_checkout_query()
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

@router.message(lambda m: m.successful_payment is not None)
async def successful_payment(message: types.Message):
    amount = message.successful_payment.total_amount
    user_id = message.from_user.id
    payload = message.successful_payment.invoice_payload

    if payload == "buy_100":
        pp_amount = 100
    elif payload == "buy_500":
        pp_amount = 500
    elif payload == "buy_1000":
        pp_amount = 1000
    else:
        pp_amount = 0

    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (telegram_id, username) VALUES (?, ?)",
            (user_id, message.from_user.username or "unknown")
        )
        await db.execute(
            "UPDATE users SET pp_balance = pp_balance + ? WHERE telegram_id = ?",
            (pp_amount, user_id)
        )
        await db.commit()

    await message.answer(f"Платёж на {amount} Stars прошёл успешно! На ваш баланс зачислено {pp_amount} PPs. Теперь вы можете играть в Mini App!")

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main()) 