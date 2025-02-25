# X Bot Blocker

Tired of all the random cornbots auto-liking your post or comments, yep, me too. 
Here's a Python bot that automatically detects and blocks spam and bot accounts interacting with your X (Twitter) posts.

## Features
- **Scans interactions** (likes, comments, follows) on your X account.
- **Analyzes accounts** for bot-like behavior using advanced detection.
- **Automatically blocks detected bot accounts.**
- **Logs blocked accounts** for review in `bot_blocker.log` and `blocked_users_log.csv`.
- **Uses rate limit handling** to prevent API bans.
- **Scheduled to run every 2 hours automatically.**
- **Designed to run locally, on cloud services, or n8n.**

## Setup Instructions

### 1. Prerequisites
- Python 3.10+
- Git
- X Developer API Access (Basic Tier is sufficient)

### 2. Clone the Repository
```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/x-bot-blocker.git
cd x-bot-blocker
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
If you experience issues, install dependencies manually:
```bash
pip install tweepy schedule pandas python-dotenv requests
```

### 4. Check and Update Dependencies
To check installed packages:
```bash
pip list
```
To update all dependencies:
```bash
pip install --upgrade tweepy schedule pandas python-dotenv requests
```

### 5. Install or Update Python (if needed)
Check your Python version:
```bash
python --version
```
If you need to install or update Python, download it from [python.org](https://www.python.org/downloads/).

### 6. Create a `.env` File (Security Best Practices)
1. Inside the `x-bot-blocker` directory, create a `.env` file:
   ```bash
   touch .env
   ```
2. Open the `.env` file and add your X API keys:
   ```
   API_KEY=your_api_key_here
   API_SECRET=your_api_secret_here
   ACCESS_TOKEN=your_access_token_here
   ACCESS_SECRET=your_access_secret_here
   ```
3. **Use `.env.example` as a reference** (do not commit real API keys).

### 7. Run the Bot
```bash
python x_bot_blocker.py
```

## Deployment Options

### Local Server Deployment
✅ Best for testing.
✅ No additional hosting costs.
⚠ Requires your computer to be running.

### Cloud Deployment
#### 🚀 Railway or Replit (Recommended for 24/7 Execution)
- Fully automated.
- Works even when your computer is off.

#### ⚡ GitHub Actions (For Scheduled Execution)
- Runs on a fixed schedule.
- No need for a separate server.

### Automating Execution in n8n
Since n8n supports HTTP requests and Python scripts, you have a couple of options:
#### **Use an n8n Workflow with API Calls (Recommended)**
✅ **Full automation inside n8n**
✅ **No additional hosting required**

🚀 **How it works:**
1. **Trigger Node** → Runs every 2 hours (or your preferred schedule).
2. **HTTP Request Node** → Fetches interactions from X API.
3. **IF Node** → Detects bot-like accounts based on predefined conditions.
4. **HTTP Request Node** → Sends POST requests to block bots.
5. **Write to Google Sheets or Notion** → Logs blocked accounts.

🔹 **What you need:**
- X API Keys
- n8n instance (self-hosted or cloud)
- Basic knowledge of n8n workflows

## Branching, Merging & Protection Rules
### **🚀 GitHub Branch Protection Rules Implemented**
To ensure code quality and security:
- **No direct commits to `main`** → All changes require pull requests.
- **Pull requests must be approved** before merging.
- **Signed commits are required** to verify authorship.
- **Force pushing is blocked** to prevent history overwrites.
- **Merge methods allowed** → Only **squash merging** (keeps history clean).
- **Conversations must be resolved** before merging.

### **🚀 Contribution Guidelines**
We encourage contributions! Read our [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Troubleshooting
### Common Errors & Fixes
**1. Authentication Errors**
- Ensure your API keys are correct.
- Verify `.env` file format.

**2. ModuleNotFoundError**
- Run `pip install -r requirements.txt` to install missing dependencies.

**3. Rate Limit Errors**
- Reduce scan frequency (e.g., every 2 hours instead of every 15 mins).

## Free X API Usage Guide
If you haven't set up an X API yet:
1. Go to [X Developer Portal](https://developer.twitter.com/).
2. Apply for **Basic Access** (free tier).
3. Create an **App** under your account.
4. Retrieve your **API keys and access tokens** from the Developer Dashboard.
5. Add these to your `.env` file.

## Future Updates & Monetization
🚀 This is the **last free version** of the X Bot Blocker. Future updates may be **paid access only**.
- Advanced AI filtering.
- Custom blocklist features.
- Rate limit optimization.
- Multi-account management.
- Automated bot reporting to X.

## Contributions
Feel free to fork this repository and submit pull requests for improvements!

## License
[MIT License](LICENSE)


## Contact
For support or questions, please:
- Open an [Issue](https://github.com/curious-keeper/x-bot-blocker/issues)


---
🚀 Happy bot-blocking!

