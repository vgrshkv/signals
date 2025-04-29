#!/usr/bin/env bash

# Install dependencies
pip install --no-cache-dir -r requirements.txt

# Run the Telegram bot
python3 -u bot/bot.py 