import tweepy
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
from collections import defaultdict
import re
from config_manager import ConfigManager

class BehaviorAnalyzer:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Load behavior analysis settings from config
        self.settings = self.config.get('behavior_analysis', {})
        
        # Default thresholds if not in config
        self.thresholds = {
            'min_interaction_interval': self.settings.get('min_interaction_interval', 1),  # seconds
            'max_interactions_per_hour': self.settings.get('max_interactions_per_hour', 50),
            'suspicious_pattern_threshold': self.settings.get('suspicious_pattern_threshold', 0.8),
            'content_similarity_threshold': self.settings.get('content_similarity_threshold', 0.9),
            'max_identical_tweets': self.settings.get('max_identical_tweets', 3)
        }

    def analyze_interaction_patterns(self, user: tweepy.User, tweets: List[tweepy.Tweet]) -> Tuple[float, List[str]]:
        """
        Analyze user's interaction patterns for bot-like behavior.
        Returns: (probability, reasons)
        """
        reasons = []
        probability = 0.0
        
        if not tweets:
            return 0.0, ["No tweets to analyze"]
            
        # Check interaction timing
        timestamps = [tweet.created_at for tweet in tweets]
        intervals = []
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i-1]).total_seconds()
            intervals.append(interval)
            
        # Check for too-regular intervals
        if intervals:
            avg_interval = sum(intervals) / len(intervals)
            std_dev = (sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)) ** 0.5
            if std_dev < self.thresholds['min_interaction_interval']:
                probability += 0.3
                reasons.append("Very regular posting intervals detected")
                
        # Check interaction frequency
        hour_counts = defaultdict(int)
        for tweet in tweets:
            hour_counts[tweet.created_at.hour] += 1
            
        max_hourly = max(hour_counts.values())
        if max_hourly > self.thresholds['max_interactions_per_hour']:
            probability += 0.3
            reasons.append(f"High interaction frequency: {max_hourly} interactions in one hour")
            
        return min(probability, 1.0), reasons

    def analyze_time_based_activity(self, user: tweepy.User, tweets: List[tweepy.Tweet]) -> Tuple[float, List[str]]:
        """
        Analyze user's activity patterns across different time periods.
        Returns: (probability, reasons)
        """
        reasons = []
        probability = 0.0
        
        if not tweets:
            return 0.0, ["No tweets to analyze"]
            
        # Check for 24/7 activity
        active_hours = set(tweet.created_at.hour for tweet in tweets)
        if len(active_hours) > 20:  # Active in more than 20 different hours
            probability += 0.4
            reasons.append("Suspicious 24/7 activity pattern detected")
            
        # Check for activity during unusual hours
        unusual_hours = set(range(2, 6))  # 2 AM to 6 AM
        if len(active_hours.intersection(unusual_hours)) > 3:
            probability += 0.3
            reasons.append("High activity during unusual hours")
            
        return min(probability, 1.0), reasons

    def analyze_network_behavior(self, user: tweepy.User) -> Tuple[float, List[str]]:
        """
        Analyze user's network behavior and connections.
        Returns: (probability, reasons)
        """
        reasons = []
        probability = 0.0
        
        # Check follower/following ratio
        if user.followers_count > 0:
            ratio = user.friends_count / user.followers_count
            if ratio > self.settings.get('max_following_ratio', 10):
                probability += 0.3
                reasons.append(f"Suspicious follower/following ratio: {ratio:.2f}")
                
        # Check for rapid follower growth
        if hasattr(user, 'created_at'):
            account_age = (datetime.now() - user.created_at).days
            if account_age > 0:
                followers_per_day = user.followers_count / account_age
                if followers_per_day > self.settings.get('max_followers_per_day', 100):
                    probability += 0.3
                    reasons.append(f"Unusual follower growth rate: {followers_per_day:.2f} per day")
                    
        return min(probability, 1.0), reasons

    def analyze_content_consistency(self, tweets: List[tweepy.Tweet]) -> Tuple[float, List[str]]:
        """
        Analyze content patterns and consistency.
        Returns: (probability, reasons)
        """
        reasons = []
        probability = 0.0
        
        if not tweets:
            return 0.0, ["No tweets to analyze"]
            
        # Check for identical tweets
        tweet_texts = [tweet.text for tweet in tweets]
        text_counts = defaultdict(int)
        for text in tweet_texts:
            text_counts[text] += 1
            
        max_identical = max(text_counts.values())
        if max_identical > self.thresholds['max_identical_tweets']:
            probability += 0.4
            reasons.append(f"Multiple identical tweets detected: {max_identical} copies")
            
        # Check for URL patterns
        url_pattern = re.compile(r'https?://\S+')
        url_counts = defaultdict(int)
        for tweet in tweets:
            urls = url_pattern.findall(tweet.text)
            for url in urls:
                url_counts[url] += 1
                
        if url_counts:
            max_url_reuse = max(url_counts.values())
            if max_url_reuse > self.thresholds['max_identical_tweets']:
                probability += 0.3
                reasons.append(f"Multiple identical URLs detected: {max_url_reuse} uses")
                
        return min(probability, 1.0), reasons

    def analyze_user(self, user: tweepy.User, tweets: List[tweepy.Tweet]) -> Tuple[float, List[str]]:
        """
        Perform comprehensive behavior analysis on a user.
        Returns: (probability, reasons)
        """
        reasons = []
        probabilities = []
        
        # Run all analysis methods
        interaction_prob, interaction_reasons = self.analyze_interaction_patterns(user, tweets)
        time_prob, time_reasons = self.analyze_time_based_activity(user, tweets)
        network_prob, network_reasons = self.analyze_network_behavior(user)
        content_prob, content_reasons = self.analyze_content_consistency(tweets)
        
        # Collect results
        probabilities.extend([interaction_prob, time_prob, network_prob, content_prob])
        reasons.extend(interaction_reasons + time_reasons + network_reasons + content_reasons)
        
        # Calculate weighted average probability
        weights = [0.3, 0.2, 0.3, 0.2]  # Weights for each analysis type
        final_probability = sum(p * w for p, w in zip(probabilities, weights))
        
        return min(final_probability, 1.0), reasons 