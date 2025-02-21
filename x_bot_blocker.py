import tweepy
import time
import logging
import pandas as pd
import schedule
import os
from datetime import datetime
from dotenv import load_dotenv

# Load API Keys from .env file
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

# Authenticate with X API
auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

# Set up logging
logging.basicConfig(
    filename="bot_blocker.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def is_bot(account):
    """Detect if an account is a bot based on set criteria."""
    if (account.default_profile_image or  # No profile picture
        account.friends_count > 1000 and account.followers_count < 50 or  # Bad ratio
        account.created_at > datetime.utcnow().replace(year=datetime.utcnow().year-1) or  # Too new
        "hot" in account.description.lower() or "dm" in account.description.lower()):  # Spam words
        return True
    return False

def scan_and_block():
    """Scans recent interactions and blocks detected bot accounts."""
    logging.info("Starting bot scan...")
    try:
        # Get latest interactions (likes, comments, follows)
        user_id = api.me().id  # Your X account ID
        likers = api.get_favorites(user_id, count=100)
        followers = api.followers(count=100)
        commenters = api.mentions_timeline(count=50)
        
        bot_accounts = []
        
        for user in set(likers + followers + [tweet.user for tweet in commenters]):
            if is_bot(user):
                logging.info(f"Blocking bot: {user.screen_name}")
                api.create_block(user.id)
                bot_accounts.append(user.screen_name)
        
        # Log blocked accounts
        if bot_accounts:
            df = pd.DataFrame(bot_accounts, columns=["Blocked Bots"])
            df.to_csv("blocked_bots.csv", mode='a', index=False, header=False)
        
        logging.info("Bot scan complete.")
    except Exception as e:
        logging.error(f"Error during scan: {e}")

# Schedule the bot to run every 2 hours
schedule.every(2).hours.do(scan_and_block)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(60)
