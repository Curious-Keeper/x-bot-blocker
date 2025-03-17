import os
import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional

class SlackReporter:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.logger = logging.getLogger('slack_reporting')

    def _send_message(self, message: Dict) -> bool:
        """Send a message to Slack"""
        if not self.webhook_url:
            self.logger.error("Slack webhook URL not configured")
            return False
            
        try:
            response = requests.post(self.webhook_url, json=message)
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to send message to Slack: {str(e)}")
            return False

    def send_daily_report(self, stats: Dict) -> None:
        """Send daily KPI report"""
        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "X Bot Blocker Daily Report",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Total Blocks:*\n{stats['total_blocks']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*False Positives:*\n{stats['false_positives']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Accuracy:*\n{stats['accuracy']:.1f}%"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*API Calls:*\n{stats['api_calls']}"
                        }
                    ]
                }
            ]
        }
        
        if stats.get('errors'):
            message["blocks"].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Recent Errors:*\n" + "\n".join(f"• {error}" for error in stats['errors'])
                }
            })
            
        self._send_message(message)

    def send_weekly_report(self, stats: Dict) -> None:
        """Send weekly summary report"""
        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "X Bot Blocker Weekly Summary",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Week of {datetime.now().strftime('%Y-%m-%d')}*"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Total Blocks:*\n{stats['total_blocks']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*False Positives:*\n{stats['false_positives']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Average Accuracy:*\n{stats['avg_accuracy']:.1f}%"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Total API Calls:*\n{stats['total_api_calls']}"
                        }
                    ]
                }
            ]
        }
        
        if stats.get('top_issues'):
            message["blocks"].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Top Issues:*\n" + "\n".join(f"• {issue}" for issue in stats['top_issues'])
                }
            })
            
        self._send_message(message)

    def send_startup_notification(self) -> None:
        """Send notification when bot starts"""
        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚀 X Bot Blocker Started",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S EST')}\n*Status:* Initializing..."
                    }
                }
            ]
        }
        self._send_message(message)

    def send_shutdown_notification(self, reason: str = "Normal shutdown") -> None:
        """Send notification when bot shuts down"""
        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🛑 X Bot Blocker Shutting Down",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S EST')}\n*Reason:* {reason}"
                    }
                }
            ]
        }
        self._send_message(message)

    def send_restart_failure_notification(self, error: str) -> None:
        """Send notification when bot fails to restart"""
        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "⚠️ X Bot Blocker Restart Failed",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S EST')}\n*Error:* {error}"
                    }
                }
            ]
        }
        self._send_message(message)

    def send_rate_limit_notification(self, limit_type: str, reset_time: str) -> None:
        """Send notification when API rate limits are hit"""
        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "⏳ X Bot Blocker Rate Limit Hit",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S EST')}\n*Limit Type:* {limit_type}\n*Resets at:* {reset_time}"
                    }
                }
            ]
        }
        self._send_message(message) 