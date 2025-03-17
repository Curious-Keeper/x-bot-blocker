import tweepy
import logging
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import yaml
import os

class BotDetector:
    def __init__(self, api: tweepy.API, config_path: str = "config.yaml"):
        self.api = api
        self.logger = logging.getLogger(__name__)
        self.load_config(config_path)
        
    def load_config(self, config_path: str):
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                detection_config = config.get('bot_detection', {})
                
                # Load detection settings
                self.min_account_age = detection_config.get('min_account_age_days', 30)
                self.min_followers = detection_config.get('min_followers', 10)
                self.max_following_ratio = detection_config.get('max_following_ratio', 10)
                self.min_tweets = detection_config.get('min_tweets', 5)
                self.bot_threshold = detection_config.get('bot_probability_threshold', 0.7)
                
                # Load whitelist/blacklist
                self.whitelist = set(detection_config.get('whitelist', []))
                self.blacklist = set(detection_config.get('blacklist', []))
                
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            # Use default values
            self.min_account_age = 30
            self.min_followers = 10
            self.max_following_ratio = 10
            self.min_tweets = 5
            self.bot_threshold = 0.7
            self.whitelist = set()
            self.blacklist = set()

    def analyze_user(self, user_id: str) -> Tuple[bool, float, str]:
        """
        Analyze a user to determine if they are a bot.
        Returns: (is_bot, probability, reason)
        """
        try:
            # Check whitelist/blacklist first
            if user_id in self.whitelist:
                return False, 0.0, "User in whitelist"
            if user_id in self.blacklist:
                return True, 1.0, "User in blacklist"

            # Get user data
            user = self.api.get_user(user_id=user_id)
            
            # Basic profile checks
            bot_score = 0.0
            reasons = []
            
            # Account age check
            created_at = user.created_at
            account_age = (datetime.now() - created_at).days
            if account_age < self.min_account_age:
                bot_score += 0.3
                reasons.append(f"New account ({account_age} days old)")
            
            # Follower count check
            if user.followers_count < self.min_followers:
                bot_score += 0.2
                reasons.append(f"Low follower count ({user.followers_count})")
            
            # Following ratio check
            if user.followers_count > 0:
                following_ratio = user.friends_count / user.followers_count
                if following_ratio > self.max_following_ratio:
                    bot_score += 0.2
                    reasons.append(f"High following ratio ({following_ratio:.1f})")
            
            # Tweet count check
            if user.statuses_count < self.min_tweets:
                bot_score += 0.2
                reasons.append(f"Low tweet count ({user.statuses_count})")
            
            # Default profile image check
            if user.default_profile_image:
                bot_score += 0.1
                reasons.append("Using default profile image")
            
            # Determine if user is a bot
            is_bot = bot_score >= self.bot_threshold
            reason = " | ".join(reasons) if reasons else "No suspicious indicators"
            
            return is_bot, bot_score, reason
            
        except tweepy.TweepyException as e:
            self.logger.error(f"Error analyzing user {user_id}: {str(e)}")
            return False, 0.0, f"Error analyzing user: {str(e)}"

    def get_recent_interactions(self, user_id: str) -> List[Dict]:
        """Get recent interactions with the user"""
        try:
            mentions = self.api.mentions_timeline(count=200)
            return [
                {
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'user_id': str(tweet.user.id)
                }
                for tweet in mentions
            ]
        except tweepy.TweepyException as e:
            self.logger.error(f"Error getting interactions for user {user_id}: {str(e)}")
            return []

    def should_block(self, user_id: str) -> Tuple[bool, str]:
        """
        Determine if a user should be blocked based on analysis.
        Returns: (should_block, reason)
        """
        is_bot, probability, reason = self.analyze_user(user_id)
        return is_bot, reason 