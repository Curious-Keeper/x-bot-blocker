#!/bin/bash

# Get the current crontab
(crontab -l 2>/dev/null | grep -v "@reboot cd /home/ubuntu/x-bot-blocker && ./launch.sh") | crontab -

# Add the new crontab entry
(crontab -l 2>/dev/null; echo "@reboot cd /home/ubuntu/x-bot-blocker && ./launch.sh") | crontab -

echo "Crontab entry added successfully" 