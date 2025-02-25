import os
import time
import logging
import tweepy
import schedule
import dotenv
import pandas as pd
from datetime import datetime

# Load environment variables
dotenv.load_dotenv()

# Twitter API Authentication
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

# Set up logging
logging.basicConfig(
    filename="bot_blocker.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Authenticate API
auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# Define bot detection criteria
BOT_CRITERIA = {
    "min_followers": 5,  # Bots usually have very few followers
    "max_following_ratio": 10,  # Following/Follower ratio (Bots often follow too many accounts)
    "min_account_age": 14,  # Days since account creation
    "spam_keywords": ["crypto", "giveaway", "DM for promo", "free followers", "click here"],
}

# Function to check if an account is a bot
def is_bot(user):
    try:
        created_at = user.created_at
        account_age_days = (datetime.utcnow() - created_at).days
        follower_count = user.followers_count
        following_count = user.friends_count
        follow_ratio = (following_count / follower_count) if follower_count > 0 else float('inf')
        username = user.screen_name.lower()
        bio = user.description.lower() if user.description else ""

        # Check criteria
        if follower_count < BOT_CRITERIA["min_followers"]:
            return True, "Low follower count"
        if follow_ratio > BOT_CRITERIA["max_following_ratio"]:
            return True, "High following/follower ratio"
        if account_age_days < BOT_CRITERIA["min_account_age"]:
            return True, "New account"
        if any(keyword in bio for keyword in BOT_CRITERIA["spam_keywords"]):
            return True, "Spam keywords detected"

        return False, "Not a bot"
    except Exception as e:
        logging.error(f"Error checking user: {e}")
        return False, "Error during check"

# Function to scan and block bots
def scan_and_block():
    try:
        logging.info("Starting bot scan...")
        blocked_users = []

        for tweet in tweepy.Cursor(api.mentions_timeline).items(100):
            user = tweet.user
            bot_detected, reason = is_bot(user)

            if bot_detected:
                api.create_block(user.id)
                blocked_users.append((user.screen_name, reason))
                logging.info(f"Blocked {user.screen_name} - Reason: {reason}")
                time.sleep(2)  # To avoid hitting rate limits

        # Save blocked users to log file
        if blocked_users:
            df = pd.DataFrame(blocked_users, columns=["Username", "Reason"])
            df.to_csv("blocked_users_log.csv", mode='a', index=False, header=False)
            logging.info("Blocked user list updated.")
        else:
            logging.info("No bots detected.")

    except tweepy.TweepError as e:
        logging.error(f"Twitter API Error: {e}")
    except Exception as e:
        logging.error(f"Unexpected Error: {e}")

# Schedule the bot to run every 2 hours
schedule.every(2).hours.do(scan_and_block)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(60)
