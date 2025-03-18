#!/bin/bash

# Change to the project directory
cd /home/ubuntu/x-bot-blocker

# Activate the virtual environment
source myenv/bin/activate

# Start the bot with nohup and redirect output to bot.log
nohup python3 src/x_bot_blocker/x_bot_blocker.py > bot.log 2>&1 &

# Save the process ID
echo $! > bot.pid

# Log the start
echo "Bot started with PID $(cat bot.pid) at $(date)" >> bot.log 