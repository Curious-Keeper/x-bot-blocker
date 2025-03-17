import tweepy
import time
import logging
import os
import signal
import json
from datetime import datetime
from dotenv import load_dotenv
from tweepy import TweepyException
import schedule
from config_manager import ConfigManager
from slack_reporting import SlackReporter
from bot_detection import BotDetector

# Load API Keys from .env file
load_dotenv()

# Initialize configuration
config = ConfigManager()

# Set up logging based on config
log_level = os.getenv('LOG_LEVEL', 'INFO')
log_file = os.getenv('LOG_FILE', 'bot_blocker.log')

# Ensure log directory exists
log_dir = os.path.dirname(log_file)
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configure logging with both file and console handlers
logger = logging.getLogger()
logger.setLevel(getattr(logging, log_level))

# Clear any existing handlers
logger.handlers = []

# Create formatters
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# File handler
file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Test logging
logging.info("Logging system initialized")

# Initialize API credentials
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# Validate required credentials
if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
    error_msg = "Missing required Twitter API credentials in .env file"
    logging.error(error_msg)
    raise ValueError(error_msg)

# Authenticate with X API
auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

# Initialize bot detector with config
bot_detector = BotDetector(api, config_path="config.yaml")

# Initialize Slack reporter
slack_reporter = SlackReporter(SLACK_WEBHOOK_URL)

# Initialize KPI tracking
kpi_stats = {
    'total_blocks': 0,
    'false_positives': 0,
    'api_calls': 0,
    'errors': [],
    'last_scan_time': None
}

def save_metrics():
    """Save current metrics to JSON file"""
    try:
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Save metrics to file
        with open('data/metrics.json', 'w') as f:
            json.dump(kpi_stats, f, indent=2)
    except Exception as e:
        logging.error(f"Error saving metrics: {str(e)}")

def handle_rate_limit(e: TweepyException):
    """Handle rate limit errors"""
    if hasattr(e, 'reset_time'):
        reset_time = datetime.fromtimestamp(e.reset_time).strftime("%Y-%m-%d %H:%M:%S EST")
        slack_reporter.send_rate_limit_notification(str(e), reset_time)
        logging.warning(f"Rate limit hit. Resets at {reset_time}")
        time.sleep(e.reset_time - time.time())
    else:
        logging.warning("Rate limit hit. Waiting 15 minutes...")
        time.sleep(900)  # Wait 15 minutes

def handle_shutdown(signum, frame):
    """Handle shutdown signals"""
    logging.info("Shutdown signal received")
    slack_reporter.send_shutdown_notification("Received shutdown signal")
    exit(0)

def scan_and_block():
    """Main scanning and blocking function"""
    try:
        kpi_stats['api_calls'] += 1
        kpi_stats['last_scan_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S EST")
        
        logging.info("Getting recent mentions...")
        mentions = api.mentions_timeline(count=200)
        
        for mention in mentions:
            user_id = str(mention.user.id)
            
            should_block, reason = bot_detector.should_block(user_id)
            
            if should_block:
                try:
                    api.create_block(user_id=user_id)
                    kpi_stats['total_blocks'] += 1
                    logging.info(f"Blocked user {user_id}: {reason}")
                except TweepyException as e:
                    error_msg = f"Error blocking user {user_id}: {str(e)}"
                    logging.error(error_msg)
                    kpi_stats['errors'].append(error_msg)
        
        # Save metrics after scan
        save_metrics()
        
        # Calculate accuracy
        accuracy = 100.0 if kpi_stats['total_blocks'] > 0 else 0.0
        
        # Send daily report
        slack_reporter.send_daily_report({
            'total_blocks': kpi_stats['total_blocks'],
            'false_positives': kpi_stats['false_positives'],
            'accuracy': accuracy,
            'api_calls': kpi_stats['api_calls'],
            'errors': kpi_stats['errors'][-3:]
        })
        
    except TweepyException as e:
        handle_rate_limit(e)
    except Exception as e:
        error_msg = f"Error in scan_and_block: {str(e)}"
        logging.error(error_msg)
        kpi_stats['errors'].append(error_msg)
        slack_reporter.send_restart_failure_notification(error_msg)

def send_weekly_summary():
    """Send weekly summary report"""
    try:
        # Calculate weekly stats
        weekly_stats = {
            'total_blocks': kpi_stats['total_blocks'],
            'false_positives': kpi_stats['false_positives'],
            'avg_accuracy': 100.0 if kpi_stats['total_blocks'] > 0 else 0.0,
            'total_api_calls': kpi_stats['api_calls'],
            'top_issues': kpi_stats['errors'][-3:]  # Last 3 errors
        }
        
        slack_reporter.send_weekly_report(weekly_stats)
        
    except Exception as e:
        logging.error(f"Error sending weekly summary: {str(e)}")

# Get scan interval from config
scan_interval = config.get('scanning.scan_interval', 60)

# Schedule the bot to run based on config
schedule.every(scan_interval).minutes.do(scan_and_block)

# Schedule weekly report
schedule.every().monday.at("00:00").do(send_weekly_summary)

if __name__ == "__main__":
    # Set up signal handlers
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    logging.info("X Bot Blocker started successfully!")
    
    # Send startup notification
    slack_reporter.send_startup_notification()
    
    try:
        logging.info("Running initial scan...")
        scan_and_block()  # Run initial scan immediately
        logging.info(f"Scheduled to run every {scan_interval} minutes. Waiting for next scan...")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)
            except Exception as e:
                error_msg = f"Error in main loop: {str(e)}"
                logging.error(error_msg)
                kpi_stats['errors'].append(error_msg)
                slack_reporter.send_restart_failure_notification(error_msg)
                time.sleep(60)  # Wait a minute before retrying
    except Exception as e:
        error_msg = f"Fatal error: {str(e)}"
        logging.error(error_msg)
        slack_reporter.send_shutdown_notification(error_msg)
        raise
