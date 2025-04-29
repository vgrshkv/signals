from fastapi import FastAPI, Request
import os
import json
import logging
from aiogram import Bot, Dispatcher, types

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
API_TOKEN = os.getenv("API_TOKEN")
GAME_SHORT_NAME = os.getenv("GAME_SHORT_NAME", "mines_hack")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, 'web')

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot=bot)

# Supported languages
LANGUAGES = {
    'en': '🇬🇧',
    'ru': '🇷🇺',
    'hi': '🇮🇳',
    'pt': '🇵🇹',
    'tr': '🇹🇷'
}

# Load locale files from bot/locales
def get_locale(lang: str) -> dict:
    path = os.path.join(BASE_DIR, 'bot', 'locales', f'{lang}.json')
    with open(path, encoding='utf-8') as f:
        return json.load(f)

# /start handler
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    locale = get_locale('en')
    kb = types.InlineKeyboardMarkup(row_width=3)
    for code, flag in LANGUAGES.items():
        kb.insert(types.InlineKeyboardButton(flag, callback_data=f'lang_{code}'))
    play_text = locale.get('play', 'Play')
    game_url = f'https://t.me/{GAME_SHORT_NAME}'
    kb.add(types.InlineKeyboardButton(play_text, url=game_url))
    photo_path = os.path.join(WEB_DIR, 'mines.png')
    with open(photo_path, 'rb') as photo:
        await message.answer_photo(photo, caption=locale.get('welcome', ''), reply_markup=kb)

# Language change handler
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('lang_'))
async def change_lang(callback_query: types.CallbackQuery):
    lang = callback_query.data.split('_', 1)[1]
    locale = get_locale(lang)
    kb = types.InlineKeyboardMarkup(row_width=3)
    for code, flag in LANGUAGES.items():
        kb.insert(types.InlineKeyboardButton(flag, callback_data=f'lang_{code}'))
    play_text = locale.get('play', 'Play')
    game_url = f'https://t.me/{GAME_SHORT_NAME}'
    kb.add(types.InlineKeyboardButton(play_text, url=game_url))
    await callback_query.message.edit_caption(caption=locale.get('welcome', ''), reply_markup=kb)
    await callback_query.answer()

# Global error handler
@dp.errors_handler()
async def handle_errors(update, exception):
    logger.exception(f"Unhandled exception in update {update}: {exception}")
    return True

# Fallback handler for unrecognized messages
@dp.message_handler()
async def fallback(message: types.Message):
    await message.reply("Команда не распознана. Попробуйте /start.")

# Create FastAPI app
app = FastAPI()

@app.on_event('startup')
async def on_startup():
    # Clear existing webhook
    await bot.delete_webhook(drop_pending_updates=True)
    # Set webhook URL if BASE_URL is provided
    base_url = os.getenv('BASE_URL')
    if base_url:
        webhook_url = f"{base_url}/{API_TOKEN}"
        await bot.set_webhook(webhook_url)
        logger.info(f"Webhook set to {webhook_url}")
    else:
        logger.warning('BASE_URL not set; skipping webhook setup')

@app.post('/{token}')
async def telegram_webhook(request: Request, token: str):
    if token != API_TOKEN:
        return {'error': 'invalid token'}
    data = await request.json()
    update = types.Update(**data)
    await dp.process_update(update)
    return {'ok': True}

@app.on_event('shutdown')
async def on_shutdown():
    await bot.delete_webhook(drop_pending_updates=True)

# For local testing via uvicorn: uvicorn main:app --reload 