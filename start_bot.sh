#!/bin/bash

# Exit on error
set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🚀 Starting X Bot Blocker and Status Server..."

# Check for config file
if [ ! -f "config.yaml" ]; then
    echo "❌ config.yaml not found!"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "myenv" ]; then
    source myenv/bin/activate
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

# Wait a moment to check if the status server is running
sleep 2
if ! kill -0 $STATUS_PID 2>/dev/null; then
    echo "❌ Status server failed to start. Check status_server.log for details."
    exit 1
fi

echo "✅ Services started successfully!"
echo "📋 Bot PID: $BOT_PID"
echo "📋 Status Server PID: $STATUS_PID"
echo "📝 Bot logs: bot_blocker.log"
echo "📝 Status server logs: status_server.log"
echo "🌐 Status server available at: http://localhost:8080"
echo "💡 To check status: curl http://localhost:8080/status"
echo "💡 To check health: curl http://localhost:8080/health"
echo "💡 To stop services: kill \$(cat bot.pid) \$(cat status.pid)"

# Keep the script running
while true; do
    if ! kill -0 $BOT_PID 2>/dev/null; then
        echo "❌ Bot process died. Restarting..."
        # Kill the status server
        kill $STATUS_PID 2>/dev/null
        
        # Start the bot again
        echo "🤖 Restarting X Bot Blocker..."
        nohup python3 src/x_bot_blocker/x_bot_blocker.py > bot_blocker.log 2>&1 &
        BOT_PID=$!
        echo $BOT_PID > bot.pid
        
        # Wait a moment for the bot to initialize
        sleep 5
        
        # Start the status server again
        echo "📊 Restarting Status Server..."
        nohup python3 src/x_bot_blocker/status_server.py > status_server.log 2>&1 &
        STATUS_PID=$!
        echo $STATUS_PID > status.pid
        
        echo "✅ Services restarted successfully!"
        echo "📋 New Bot PID: $BOT_PID"
        echo "📋 New Status Server PID: $STATUS_PID"
    fi
    if ! kill -0 $STATUS_PID 2>/dev/null; then
        echo "❌ Status server died. Restarting..."
        # Kill the bot
        kill $BOT_PID 2>/dev/null
        
        # Start the status server again
        echo "📊 Restarting Status Server..."
        nohup python3 src/x_bot_blocker/status_server.py > status_server.log 2>&1 &
        STATUS_PID=$!
        echo $STATUS_PID > status.pid
        
        echo "✅ Status Server restarted successfully!"
        echo "📋 New Status Server PID: $STATUS_PID"
    fi
    sleep 5
done 