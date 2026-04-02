import os
import requests
import json
import smtplib
from email.message import EmailMessage
from datetime import datetime
from dotenv import load_dotenv

# 1. Load your Secrets
load_dotenv()
NEWS_KEY = os.getenv("NEWS_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
SENDER = os.getenv("SENDER_EMAIL")
PASSWORD = os.getenv("EMAIL_PASS")
RECEIVER = os.getenv("RECEIVER_EMAIL")

def get_tech_news():
    """Fetch headlines from NewsAPI"""
    url = f"https://newsapi.org/v2/top-headlines?category=technology&language=en&apiKey={NEWS_KEY}"
    response = requests.get(url).json()
    articles = response.get("articles", [])[:10]
    
    news_string = ""
    for a in articles:
        # Use .get() to avoid errors if a title is missing
        title = a.get('title', 'No Title')
        news_string += f"- {title}\n"
    return news_string

def summarize_with_gemini(text):
    """Direct POST request to Gemini V1 Stable API"""
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": f"Summarize these tech headlines into a professional briefing. Focus on launches and big tech updates:\n\n{text}"}]
        }]
    }
    
    headers = {'Content-Type': 'application/json'}
    # We use response.text to ensure we get a string
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code != 200:
        return f"AI Summary Error: {response.status_code} - {response.text}"
    
    result = response.json()
    
    try:
        # We force the output to be a string to avoid the TypeError
        summary_text = str(result['candidates'][0]['content']['parts'][0]['text'])
        return summary_text
    except (KeyError, IndexError):
        return "Error: Could not parse the AI response. Check API logs."

def send_email(body):
    """Send the final email via Gmail"""
    # Force body to string just in case
    content = str(body)
    
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = f"🚀 Tech Daily: {datetime.now().strftime('%d %b %Y')}"
    msg['From'] = SENDER
    msg['To'] = RECEIVER

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(SENDER, PASSWORD)
        smtp.send_message(msg)

if __name__ == "__main__":
    print("Step 1: Fetching News...")
    raw_news = get_tech_news()
    
    print("Step 2: Summarizing with Gemini...")
    summary = summarize_with_gemini(raw_news)
    
    print("Step 3: Sending Email...")
    send_email(summary)
    print("Success! Check your inbox.")
