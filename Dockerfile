# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install build dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Expose default port (unused but standard)
EXPOSE 8000

# Start the bot
CMD ["python3", "-u", "bot/bot.py"] 