#!/usr/bin/env bash
# Load environment variables if present
if [ -f "$HOME/.signals_env" ]; then
  source "$HOME/.signals_env"
fi
set -e
# Ensure we are in HOME to prevent cwd errors
cd "$HOME"

# Скрипт автоматического деплоя проекта Signals на Ubuntu сервере
# Перед запуском убедитесь, что на сервере доступны git, python3 и sudo.

# Переменные (можно переопределить при запуске):
REPO_URL="https://github.com/vgrshkv/signals.git"
APP_DIR="/home/ubuntu/signals"
ENV_FILE="$APP_DIR/bot/.env"
GAME_SHORT_NAME="mines_hack"

# Токен бота расскажите через переменную окружения или введите здесь:
# export API_TOKEN="<ваш_токен>"

# Обновление системы и установка зависимостей
sudo apt update && sudo apt install -y git python3 python3-venv python3-pip

# Клонирование репозитория: удаляем старую копию (если есть) и делаем свежий клон
if [ -d "$APP_DIR" ]; then
  sudo rm -rf "$APP_DIR"
fi
git clone --single-branch --branch main "$REPO_URL" "$APP_DIR"
cd "$APP_DIR"

# Подготовка .env для Telegram бота
if [ -z "$API_TOKEN" ]; then
  echo "Ошибка: API_TOKEN не задан. Задайте export API_TOKEN перед запуском скрипта." >&2
  exit 1
fi
mkdir -p "$(dirname "$ENV_FILE")"
cat > "$ENV_FILE" <<EOF
API_TOKEN=$API_TOKEN
GAME_SHORT_NAME=$GAME_SHORT_NAME
EOF

echo ".env файл создан в $ENV_FILE"

## Setup single Python virtual environment
if [ ! -d venv ]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
# Install all dependencies from requirements.txt
pip install -r requirements.txt
deactivate

## Запуск FastAPI приложения в фоне
pkill -f "uvicorn main:app" || true
nohup venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &
echo "FastAPI запущен на порту 8000"

## Запуск Telegram бота в фоне
pkill -f "bot.py" || true
# Start the bot using the venv's Python binary
nohup venv/bin/python bot/bot.py > bot.log 2>&1 &
echo "Telegram бот запущен (polling)"

# Доступные логи:
echo "Логи FastAPI: $APP_DIR/uvicorn.log"
echo "Логи бота:   $APP_DIR/bot.log"

echo "Деплой завершён. Проверяйте сервисы и логи." 