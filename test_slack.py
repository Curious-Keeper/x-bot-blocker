import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get webhook URL
webhook_url = os.getenv('SLACK_WEBHOOK_URL')
print(f"Webhook URL: {webhook_url}")

if not webhook_url:
    print("Error: SLACK_WEBHOOK_URL not found in environment")
    exit(1)

# Test message
message = {
    "blocks": [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🔔 Test Notification",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "This is a test notification from the X Bot Blocker."
            }
        }
    ]
}

print("Sending message to Slack...")
try:
    response = requests.post(webhook_url, json=message)
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")
    response.raise_for_status()
    print("Test notification sent successfully!")
except Exception as e:
    print(f"Error sending notification: {str(e)}") 