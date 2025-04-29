import os
import logging
import asyncio
from flask import Flask, request
from aiogram import Bot, Dispatcher, types

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot and Dispatcher
API_TOKEN = os.getenv('API_TOKEN')
assert API_TOKEN, "API_TOKEN environment variable is required"
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Supported languages and flags
LANGUAGES = {
    'en': '🇬🇧',
    'ru': '🇷🇺',
    'hi': '🇮🇳',
    'pt': '🇵🇹',
    'tr': '🇹🇷'
}

# Load locales from JSON files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCALES_DIR = os.path.join(BASE_DIR, 'bot', 'locales')

def get_locale(lang: str) -> dict:
    path = os.path.join(LOCALES_DIR, f'{lang}.json')
    with open(path, encoding='utf-8') as f:
        return json.load(f)

# Handler for /start command
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    locale = get_locale('en')
    kb = types.InlineKeyboardMarkup(row_width=3)
    for code, flag in LANGUAGES.items():
        kb.insert(types.InlineKeyboardButton(flag, callback_data=f'lang_{code}'))
    play_text = locale.get('play', 'Play')
    game_url = f"https://{os.getenv('PA_HOSTNAME')}.pythonanywhere.com/signal.html"
    kb.add(types.InlineKeyboardButton(play_text, url=game_url))
    photo_path = os.path.join(BASE_DIR, 'web', 'mines.png')
    with open(photo_path, 'rb') as photo:
        await message.answer_photo(photo, caption=locale.get('welcome', ''), reply_markup=kb)

# Handler for language change callbacks
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('lang_'))
async def change_lang(callback_query: types.CallbackQuery):
    lang = callback_query.data.split('_', 1)[1]
    locale = get_locale(lang)
    kb = types.InlineKeyboardMarkup(row_width=3)
    for code, flag in LANGUAGES.items():
        kb.insert(types.InlineKeyboardButton(flag, callback_data=f'lang_{code}'))
    play_text = locale.get('play', 'Play')
    game_url = f"https://{os.getenv('PA_HOSTNAME')}.pythonanywhere.com/signal.html"
    kb.add(types.InlineKeyboardButton(play_text, url=game_url))
    await callback_query.message.edit_caption(caption=locale.get('welcome', ''), reply_markup=kb)
    await callback_query.answer()

# Global error handler
@dp.errors_handler()
async def handle_errors(update, exception):
    logger.exception(f"Unhandled exception in update {update}: {exception}")
    return True

# Create Flask app
def create_app():
    app = Flask(__name__)

    # Telegram webhook route
    @app.route(f"/{API_TOKEN}", methods=['POST'])
    def webhook():
        update = types.Update(**request.get_json())
        asyncio.get_event_loop().create_task(dp.process_update(update))
        return '', 200

    return app

# Setup webhook on startup
async def on_startup():
    await bot.delete_webhook(drop_pending_updates=True)
    webhook_url = f"https://{os.getenv('PA_HOSTNAME')}.pythonanywhere.com/{API_TOKEN}"
    await bot.set_webhook(webhook_url)
    logger.info(f"Webhook set to {webhook_url}")

# Run setup
asyncio.get_event_loop().run_until_complete(on_startup())

# Expose Flask app for WSGI
application = create_app() 