# X Bot Blocker

Tired of all the random cornbots auto-liking your post or comments, yep, me too. 
Here's a Python bot that automatically detects and blocks spam and bot accounts interacting with your X (Twitter) posts.

## Features
- **Scans interactions** (likes, comments, follows) on your X account.
- **Analyzes accounts** for bot-like behavior.
- **Automatically blocks detected bot accounts.**
- **Logs blocked accounts** for review.
- **Designed to run locally or on cloud services.**

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
**Why use a `.env` file?**
- Keeps API keys secure when hosting publicly.
- Prevents accidental exposure in GitHub.
- Always add `.env` to `.gitignore` to keep it private.

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

## Testing the Bot
### Local Testing
✅ Run the bot manually:
```bash
python x_bot_blocker.py
```
✅ Check logs to see which accounts were detected.

### Cloud Testing
✅ Deploy to **Railway.app** or **Replit**.
✅ Run logs to verify behavior.

## Choosing the Right Deployment Option
🚀 **For an always-running bot** → Use **Railway.app** or **Replit**.
💻 **For manual execution** → Run locally as needed.
⚡ **For scheduled automation** → Use **GitHub Actions**.

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

## Future Updates
- More deployment options may be introduced based on user feedback.

## Contributions
Feel free to fork this repository and submit pull requests for improvements!

## License
[MIT License](LICENSE)

## Contact
For support or questions, please:
- Open an [Issue](https://github.com/curious-keeper/x-bot-blocker/issues)


---
🚀 Happy bot-blocking!

