# X Bot Blocker

A powerful and accurate bot detection and blocking system for X (Twitter) that protects users from automated accounts, spam, and malicious bots while maintaining high accuracy and minimal false positives.

## Features

### Core Features
- 🔍 **Advanced Bot Detection**
  - Profile analysis
  - Content analysis
  - Image analysis
  - Pattern recognition
  - Language detection
  - Behavior analysis

- 🛡️ **Protection**
  - Automated blocking
  - Rate limit management
  - Whitelist/blacklist support
  - Block history tracking

- ⚙️ **Configuration**
  - YAML-based settings
  - Hot-reload support
  - Environment variables
  - Customizable thresholds

### Current Status
- ✅ Phase 1: Foundation (Completed)
  - Configuration Management
  - Blocked Accounts Tracking
  - Rate Limit Optimization
- 🔄 Phase 2: Core Enhancement (In Progress)
  - Enhanced Bot Detection
  - Monitoring & Alerts

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/x-bot-blocker.git
cd x-bot-blocker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your X API credentials
```

4. Configure settings:
```bash
cp config.yaml.example config.yaml
# Edit config.yaml with your preferences
```

## Usage

1. Start the bot:
```bash
python x_bot_blocker.py
```

2. Monitor the logs:
```bash
tail -f bot_blocker.log
```

3. Export blocked accounts:
```bash
python export_blocked.py
```

## Configuration

The bot uses a YAML configuration file (`config.yaml`) for settings:

```yaml
api:
  rate_limit:
    max_blocks_per_day: 1000
    cooldown_period: 60

bot_detection:
  min_account_age_days: 30
  min_followers: 10
  max_following_ratio: 10
  min_tweets: 5
  bot_probability_threshold: 0.7

scanning:
  mentions_count: 200
  followers_count: 200
  likes_count: 200
  scan_interval: 60
```

## Development

### Project Structure
```
x-bot-blocker/
├── config.yaml           # Configuration settings
├── requirements.txt      # Python dependencies
├── x_bot_blocker.py      # Main bot script
├── config_manager.py     # Configuration management
├── bot_detection.py      # Bot detection logic
├── image_analysis.py     # Image analysis module
└── blocked_accounts.csv  # Blocked accounts database
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

### Testing
```bash
python -m pytest tests/
```

## Documentation

- [Core Focus](CORE_FOCUS.md) - Project goals and scope
- [Implementation Plan](implementation_plan.md) - Development roadmap
- [API Documentation](docs/api.md) - API reference
- [User Guide](docs/user_guide.md) - Usage instructions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please:
1. Check the [documentation](docs/)
2. Search [existing issues](issues/)
3. Create a new issue if needed

## Acknowledgments

- X API for providing the platform
- OpenCV for image analysis
- LangDetect for language detection
- All contributors and users
