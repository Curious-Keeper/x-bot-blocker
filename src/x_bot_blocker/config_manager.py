import yaml
import os
from typing import Dict, Any, List
import logging
from datetime import datetime

class ConfigManager:
    def __init__(self, config_path: str = "config.yaml"):
        # Get the project root directory (two levels up from this file)
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # Always use absolute path for config file
        self.config_path = os.path.join(self.project_root, config_path) if not os.path.isabs(config_path) else config_path
        self.config: Dict[str, Any] = {}
        self.last_modified: float = 0
        self.load_config()
        logging.info(f"Using config file at: {self.config_path}")

    def load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = yaml.safe_load(f)
                self.last_modified = os.path.getmtime(self.config_path)
                logging.info(f"Configuration loaded successfully from {self.config_path}")
            else:
                logging.error(f"Configuration file not found: {self.config_path}")
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")
            raise

    def check_for_updates(self) -> bool:
        """Check if configuration file has been modified."""
        try:
            current_modified = os.path.getmtime(self.config_path)
            if current_modified > self.last_modified:
                self.load_config()
                return True
            return False
        except Exception as e:
            logging.error(f"Error checking configuration updates: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        try:
            keys = key.split('.')
            value = self.config
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation."""
        try:
            keys = key.split('.')
            current = self.config
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            current[keys[-1]] = value
            self.save_config()
        except Exception as e:
            logging.error(f"Error setting configuration: {e}")
            raise

    def save_config(self) -> None:
        """Save configuration to YAML file."""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            self.last_modified = os.path.getmtime(self.config_path)
            logging.info("Configuration saved successfully")
        except Exception as e:
            logging.error(f"Error saving configuration: {e}")
            raise

    def add_to_whitelist(self, username: str) -> None:
        """Add username to whitelist."""
        whitelist = self.get('lists.whitelist', [])
        if username not in whitelist:
            whitelist.append(username)
            self.set('lists.whitelist', whitelist)
            logging.info(f"Added {username} to whitelist")

    def add_to_blacklist(self, username: str) -> None:
        """Add username to blacklist."""
        blacklist = self.get('lists.blacklist', [])
        if username not in blacklist:
            blacklist.append(username)
            self.set('lists.blacklist', blacklist)
            logging.info(f"Added {username} to blacklist")

    def remove_from_whitelist(self, username: str) -> None:
        """Remove username from whitelist."""
        whitelist = self.get('lists.whitelist', [])
        if username in whitelist:
            whitelist.remove(username)
            self.set('lists.whitelist', whitelist)
            logging.info(f"Removed {username} from whitelist")

    def remove_from_blacklist(self, username: str) -> None:
        """Remove username from blacklist."""
        blacklist = self.get('lists.blacklist', [])
        if username in blacklist:
            blacklist.remove(username)
            self.set('lists.blacklist', blacklist)
            logging.info(f"Removed {username} from blacklist")

    def is_whitelisted(self, username: str) -> bool:
        """Check if username is in whitelist."""
        return username in self.get('lists.whitelist', [])

    def is_blacklisted(self, username: str) -> bool:
        """Check if username is in blacklist."""
        return username in self.get('lists.blacklist', [])

    def get_spam_words(self) -> List[str]:
        """Get list of spam words."""
        return self.get('detection.spam_words', [])

    def get_rate_limits(self) -> Dict[str, Any]:
        """Get rate limit settings."""
        return self.get('api.rate_limit', {})

    def get_scanning_settings(self) -> Dict[str, Any]:
        """Get scanning settings."""
        return self.get('scanning', {})

    def get_reporting_settings(self) -> Dict[str, Any]:
        """Get reporting settings."""
        return self.get('reporting', {}) 