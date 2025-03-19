#!/bin/bash

# Exit on error
set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🛑 Stopping X Bot Blocker and Status Server..."

# Function to check if a process is running
is_process_running() {
    local pid=$1
    if kill -0 $pid 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to gracefully stop a process
stop_process() {
    local pid=$1
    local name=$2
    
    if is_process_running $pid; then
        echo "Stopping $name (PID: $pid)..."
        kill $pid
        
        # Wait up to 10 seconds for the process to stop
        for i in {1..10}; do
            if ! is_process_running $pid; then
                echo "✅ $name stopped successfully"
                return 0
            fi
            sleep 1
        done
        
        # If process is still running, force kill it
        if is_process_running $pid; then
            echo "Force stopping $name..."
            kill -9 $pid
            echo "✅ $name force stopped"
        fi
    else
        echo "❌ $name is not running"
    fi
}

# First, stop the monitoring loop in start_bot.sh
echo "Stopping monitoring loop..."
pkill -f "start_bot.sh" || true
sleep 2  # Give it a moment to stop

# Read PIDs from files if they exist
if [ -f "bot.pid" ]; then
    BOT_PID=$(cat bot.pid)
    stop_process $BOT_PID "X Bot Blocker"
    rm -f bot.pid
fi

if [ -f "status.pid" ]; then
    STATUS_PID=$(cat status.pid)
    stop_process $STATUS_PID "Status Server"
    rm -f status.pid
fi

# Double check for any remaining processes
BOT_PROCESS=$(pgrep -f "python.*x_bot_blocker.py" || true)
STATUS_PROCESS=$(pgrep -f "python.*status_server.py" || true)
MONITOR_PROCESS=$(pgrep -f "start_bot.sh" || true)

if [ ! -z "$BOT_PROCESS" ]; then
    echo "Found remaining bot process, stopping..."
    kill -9 $BOT_PROCESS
fi

if [ ! -z "$STATUS_PROCESS" ]; then
    echo "Found remaining status server process, stopping..."
    kill -9 $STATUS_PROCESS
fi

if [ ! -z "$MONITOR_PROCESS" ]; then
    echo "Found remaining monitoring process, force stopping..."
    kill -9 $MONITOR_PROCESS
fi

# Final verification
if pgrep -f "x_bot_blocker.py" > /dev/null || \
   pgrep -f "status_server.py" > /dev/null || \
   pgrep -f "start_bot.sh" > /dev/null; then
    echo "⚠️ Some processes are still running. Attempting final cleanup..."
    pkill -9 -f "x_bot_blocker.py"
    pkill -9 -f "status_server.py"
    pkill -9 -f "start_bot.sh"
fi

# Verify all processes are stopped
if ! pgrep -f "x_bot_blocker.py" > /dev/null && \
   ! pgrep -f "status_server.py" > /dev/null && \
   ! pgrep -f "start_bot.sh" > /dev/null; then
    echo "✅ All services stopped successfully!"
else
    echo "⚠️ Some processes may still be running. Please check manually."
    exit 1
fi 