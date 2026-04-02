# ⚡ Tech Briefing Agent

Fetches the latest tech updates using **Claude + Web Search** and delivers them
via **Email** and/or **Slack** every day at **6:00 AM IST**.

---

## 📁 Files

```
tech_briefing_agent/
├── briefing_agent.py   # Main script
├── config.py           # Topics, API keys, delivery settings
├── .env.example        # Environment variable template
├── requirements.txt    # Python dependencies
└── briefings/          # Auto-created; saved briefing .txt files
```

---

## 🚀 Quick Setup (5 minutes)

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure your environment

```bash
cp .env.example .env
```

Edit `.env` and fill in:
- `ANTHROPIC_API_KEY` — from https://console.anthropic.com
- Email and/or Slack settings (both are optional)

### 3. Load your .env

Add this to the top of `briefing_agent.py` (already included):
```python
from dotenv import load_dotenv
load_dotenv()
```

### 4. Test it manually

```bash
python briefing_agent.py
```

You should see the briefing printed and saved to `briefings/`.

---

## ⏰ Scheduling at 6:00 AM IST

6:00 AM IST = **00:30 UTC**

### Option A — cron (Linux/macOS)

```bash
crontab -e
```

Add this line:
```
30 0 * * * cd /path/to/tech_briefing_agent && /usr/bin/python3 briefing_agent.py >> briefings/cron.log 2>&1
```

### Option B — GitHub Actions (cloud, free)

Create `.github/workflows/briefing.yml` in any GitHub repo:

```yaml
name: Daily Tech Briefing

on:
  schedule:
    - cron: '30 0 * * *'   # 6:00 AM IST = 00:30 UTC
  workflow_dispatch:        # allow manual runs

jobs:
  briefing:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: python briefing_agent.py
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          EMAIL_ENABLED: 'true'
          EMAIL_SENDER: ${{ secrets.EMAIL_SENDER }}
          EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
          EMAIL_RECIPIENTS: ${{ secrets.EMAIL_RECIPIENTS }}
          SLACK_ENABLED: 'true'
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

Add secrets at: **Repo → Settings → Secrets and variables → Actions**

### Option C — Google Cloud Scheduler + Cloud Run

1. Containerize the script with Docker
2. Deploy to Cloud Run
3. Set a Cloud Scheduler job at `30 0 * * *` (UTC)

---

## 📧 Gmail Setup

1. Enable 2FA on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Generate an App Password for "Mail"
4. Use that 16-char password as `EMAIL_PASSWORD`

> **Do NOT use your real Gmail password.**

---

## 💬 Slack Setup

1. Go to https://api.slack.com/messaging/webhooks
2. Click "Create your Slack app" → "Incoming Webhooks"
3. Activate and add to a channel
4. Copy the webhook URL to `SLACK_WEBHOOK_URL`

---

## 🎛 Customising Topics

Edit `config.py` → `topics` list:

```python
topics: list[str] = [
    "🤖 AI & Machine Learning",
    "🌐 Web Development",
    "☁️  Cloud & DevOps",
    "🦀 Rust ecosystem updates",
    "📱 Mobile (iOS/Android)",
]
```

---

## 💾 Local Archive

Every run saves a timestamped `.txt` file in `briefings/`:
```
briefings/briefing_Monday_07_April_2025_06-00.txt
```
