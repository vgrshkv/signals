import os
import json
from aiogram.utils import executor
from aiogram import Bot, Dispatcher, types
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_TOKEN = os.getenv('API_TOKEN', '8059789021:AAGwqdPR_cF_Z1VbDooFimdmzcWIbwpd5nk')
# Короткое имя мини-приложения, настроенное в BotFather
GAME_SHORT_NAME = os.getenv('GAME_SHORT_NAME', 'mines_hack')
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
WEB_DIR = os.path.join(PROJECT_ROOT, 'web')

# Поддерживаемые языки и флаги
LANGUAGES = {
    'en': '🇬🇧',
    'ru': '🇷🇺',
    'hi': '🇮🇳',
    'pt': '🇵🇹',
    'tr': '🇹🇷'
}

# Загрузка локалей из файлов
def get_locale(lang: str) -> dict:
    path = os.path.join(BASE_DIR, 'locales', f'{lang}.json')
    with open(path, encoding='utf-8') as f:
        return json.load(f)

# Обработчик /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    logger.info(f"Received /start from user {message.from_user.id}")
    locale = get_locale('en')
    kb = types.InlineKeyboardMarkup(row_width=3)
    for code, flag in LANGUAGES.items():
        kb.insert(types.InlineKeyboardButton(flag, callback_data=f'lang_{code}'))
    play_text = locale.get('play', 'Play')
    game_url = 'https://t.me/mineshacker1win_bot/mines_hack'
    kb.add(types.InlineKeyboardButton(play_text, url=game_url))
    photo_path = os.path.join(WEB_DIR, 'mines.png')
    with open(photo_path, 'rb') as photo:
        await message.answer_photo(photo, caption=locale.get('welcome', ''), reply_markup=kb)

# Обработчик статуса языка
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('lang_'))
async def change_lang(callback_query: types.CallbackQuery):
    logger.info(f"Language change callback: {callback_query.data}")
    lang = callback_query.data.split('_', 1)[1]
    locale = get_locale(lang)
    kb = types.InlineKeyboardMarkup(row_width=3)
    for code, flag in LANGUAGES.items():
        kb.insert(types.InlineKeyboardButton(flag, callback_data=f'lang_{code}'))
    play_text = locale.get('play', 'Play')
    game_url = 'https://t.me/mineshacker1win_bot/mines_hack'
    kb.add(types.InlineKeyboardButton(play_text, url=game_url))
    await callback_query.message.edit_caption(caption=locale.get('welcome', ''), reply_markup=kb)
    await callback_query.answer()

# Add a global error handler to catch and log exceptions
@dp.errors_handler()
async def handle_errors(update, exception):
    logger.exception(f"Unhandled exception in update {update}: {exception}")
    return True

# Add a startup hook to clear any existing webhook
async def on_startup(dp):
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info('Webhook cleared, pending updates dropped')

# Add fallback handler to catch any unhandled messages and help debug
@dp.message_handler()
async def fallback(message: types.Message):
    logger.info(f"Received unhandled message: {message.text}")
    await message.reply("Команда не распознана. Попробуйте /start.")

if __name__ == '__main__':
    logger.info('Starting polling of Telegram updates')
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup) 