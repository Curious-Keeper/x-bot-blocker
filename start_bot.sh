#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting X Bot Blocker and Status Server..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start the bot
echo "🤖 Starting X Bot Blocker..."
nohup python3 src/x_bot_blocker/x_bot_blocker.py > bot_blocker.log 2>&1 &
BOT_PID=$!
echo $BOT_PID > bot.pid

# Wait a moment for the bot to initialize
sleep 5

# Start the status server
echo "📊 Starting Status Server..."
nohup python3 src/x_bot_blocker/status_server.py > status_server.log 2>&1 &
STATUS_PID=$!
echo $STATUS_PID > status.pid

echo "✅ Services started successfully!"
echo "📋 Bot PID: $BOT_PID"
echo "📋 Status Server PID: $STATUS_PID"
echo "📝 Bot logs: bot_blocker.log"
echo "📝 Status server logs: status_server.log"
echo "🌐 Status server available at: http://localhost:8080"
echo "💡 To check status: curl http://localhost:8080/status"
echo "💡 To check health: curl http://localhost:8080/health"
echo "💡 To stop services: kill \$(cat bot.pid) \$(cat status.pid)" 