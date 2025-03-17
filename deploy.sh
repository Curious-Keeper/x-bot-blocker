#!/bin/bash

# Exit on error
set -e

echo "🚀 Deploying X Bot Blocker..."

# Check Python version
python3 --version

# Create and activate virtual environment
echo "📦 Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your API credentials and Slack webhook URL."
    exit 1
fi

# Check for config.yaml
if [ ! -f config.yaml ]; then
    echo "❌ Error: config.yaml not found!"
    echo "Please create a config.yaml file with your settings."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data/blocked

# Set up logging
echo "📝 Setting up logging..."
touch logs/bot_blocker.log

# Test the bot
echo "🧪 Running tests..."
python -m pytest tests/

# Start the bot
echo "🤖 Starting X Bot Blocker..."
nohup python src/x_bot_blocker/x_bot_blocker.py > logs/bot_blocker.log 2>&1 &

# Get the process ID
BOT_PID=$!

# Save the PID
echo $BOT_PID > bot.pid

echo "✅ Deployment complete!"
echo "📋 Bot is running with PID: $BOT_PID"
echo "📝 Logs are being written to: logs/bot_blocker.log"
echo "💡 To stop the bot, run: kill $(cat bot.pid)" 