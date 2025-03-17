import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import tweepy
from langdetect import detect, LangDetectException
from config_manager import ConfigManager
from image_analysis import ImageAnalyzer
from behavior_analysis import BehaviorAnalyzer

class BotDetector:
    def __init__(self, api: tweepy.API, config: ConfigManager):
        self.api = api
        self.config = config
        self.logger = logging.getLogger('bot_detection')
        
        # Load detection settings
        self.min_account_age = config.get('detection.min_account_age', 30)
        self.min_followers = config.get('detection.min_followers', 10)
        self.max_following_ratio = config.get('detection.max_following_ratio', 10)
        self.min_tweets = config.get('detection.min_tweets', 5)
        self.bot_threshold = config.get('detection.bot_probability_threshold', 0.7)
        
        # Load whitelist/blacklist
        self.whitelist = set(config.get('lists.whitelist', []))
        self.blacklist = set(config.get('lists.blacklist', []))

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
        Determine if a user should be blocked.
        Returns: (should_block, reason)
        """
        is_bot, probability, reason = self.analyze_user(user_id)
        
        if is_bot:
            return True, f"Bot detected (probability: {probability:.2f}) - {reason}"
        
        return False, f"Not a bot (probability: {probability:.2f}) - {reason}"

class EnhancedBotDetection:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize analyzers
        self.image_analyzer = ImageAnalyzer(config) if config.get('image_analysis', {}).get('enabled', False) else None
        self.behavior_analyzer = BehaviorAnalyzer(config)
        
        # Load detection settings
        self.settings = self.config.get('bot_detection', {})
        self.thresholds = {
            'min_account_age_days': self.settings.get('min_account_age_days', 30),
            'min_followers': self.settings.get('min_followers', 10),
            'max_following_ratio': self.settings.get('max_following_ratio', 10),
            'min_tweets': self.settings.get('min_tweets', 5),
            'bot_probability_threshold': self.settings.get('bot_probability_threshold', 0.7)
        }
        
        # Load spam words
        self.spam_words = set(self.settings.get('spam_words', []))
        
        # Load patterns from config
        self.suspicious_patterns = self.config.get('bot_detection.suspicious_patterns', [])
        self.url_patterns = self.config.get('bot_detection.url_patterns', [])
        
    def analyze_user(self, user: tweepy.User, tweets: List[tweepy.Tweet]) -> Tuple[float, List[str]]:
        """
        Perform comprehensive analysis of a user account.
        Returns: (probability, reasons)
        """
        reasons = []
        probabilities = []
        
        # Basic profile analysis
        profile_prob, profile_reasons = self.analyze_profile(user)
        probabilities.append(profile_prob)
        reasons.extend(profile_reasons)
        
        # Content analysis
        content_prob, content_reasons = self.analyze_content(tweets)
        probabilities.append(content_prob)
        reasons.extend(content_reasons)
        
        # Image analysis if enabled
        if self.image_analyzer:
            image_prob, image_reasons = self.image_analyzer.analyze_profile_image(user)
            probabilities.append(image_prob)
            reasons.extend(image_reasons)
            
        # Behavior analysis
        behavior_prob, behavior_reasons = self.behavior_analyzer.analyze_user(user, tweets)
        probabilities.append(behavior_prob)
        reasons.extend(behavior_reasons)
        
        # Calculate weighted average probability
        weights = [0.2, 0.2, 0.2, 0.4]  # Weights for each analysis type
        final_probability = sum(p * w for p, w in zip(probabilities, weights))
        
        return min(final_probability, 1.0), reasons

    def analyze_profile(self, user: tweepy.User) -> Tuple[float, List[str]]:
        """
        Analyze user profile for bot-like characteristics.
        Returns: (probability, reasons)
        """
        reasons = []
        probability = 0.0
        
        # Check account age
        if hasattr(user, 'created_at'):
            account_age = (datetime.now() - user.created_at).days
            if account_age < self.thresholds['min_account_age_days']:
                probability += 0.3
                reasons.append(f"New account: {account_age} days old")
                
        # Check follower count
        if user.followers_count < self.thresholds['min_followers']:
            probability += 0.2
            reasons.append(f"Low follower count: {user.followers_count}")
            
        # Check following ratio
        if user.followers_count > 0:
            ratio = user.friends_count / user.followers_count
            if ratio > self.thresholds['max_following_ratio']:
                probability += 0.3
                reasons.append(f"Suspicious following ratio: {ratio:.2f}")
                
        # Check tweet count
        if user.statuses_count < self.thresholds['min_tweets']:
            probability += 0.2
            reasons.append(f"Low tweet count: {user.statuses_count}")
            
        return min(probability, 1.0), reasons

    def analyze_content(self, tweets: List[tweepy.Tweet]) -> Tuple[float, List[str]]:
        """
        Analyze user's content for spam and bot-like patterns.
        Returns: (probability, reasons)
        """
        reasons = []
        probability = 0.0
        
        if not tweets:
            return 0.0, ["No tweets to analyze"]
            
        # Check for spam words
        spam_count = 0
        for tweet in tweets:
            text = tweet.text.lower()
            for word in self.spam_words:
                if word.lower() in text:
                    spam_count += 1
                    
        if spam_count > 0:
            probability += min(0.4, spam_count * 0.1)
            reasons.append(f"Spam words detected in {spam_count} tweets")
            
        # Check for URL patterns
        url_pattern = re.compile(r'https?://\S+')
        url_count = 0
        for tweet in tweets:
            if url_pattern.search(tweet.text):
                url_count += 1
                
        if url_count > len(tweets) * 0.7:  # More than 70% of tweets contain URLs
            probability += 0.3
            reasons.append(f"High URL frequency: {url_count}/{len(tweets)} tweets")
            
        return min(probability, 1.0), reasons

    def _check_username_patterns(self, username: str) -> bool:
        """Check username against suspicious patterns."""
        for pattern in self.suspicious_patterns:
            if re.search(pattern, username):
                return True
        return False
    
    def _analyze_description(self, description: str) -> Dict[str, any]:
        """Analyze user description for suspicious content."""
        analysis = {
            'is_suspicious': False,
            'reasons': []
        }
        
        # Check for spam words
        for word in self.spam_words:
            if word.lower() in description.lower():
                analysis['is_suspicious'] = True
                analysis['reasons'].append(f"Contains spam word: {word}")
        
        # Check for URL patterns
        for pattern in self.url_patterns:
            if re.search(pattern, description):
                analysis['is_suspicious'] = True
                analysis['reasons'].append("Contains suspicious URL pattern")
        
        # Try to detect language
        try:
            lang = detect(description)
            if lang not in ['en', 'es']:  # Add more languages as needed
                analysis['is_suspicious'] = True
                analysis['reasons'].append(f"Suspicious language detected: {lang}")
        except LangDetectException:
            pass
        
        return analysis
    
    def is_bot(self, user: tweepy.User, tweets: List[tweepy.Tweet]) -> Tuple[bool, List[str]]:
        """
        Determine if a user is likely a bot.
        Returns: (is_bot, reasons)
        """
        probability, reasons = self.analyze_user(user, tweets)
        return probability >= self.thresholds['bot_probability_threshold'], reasons 