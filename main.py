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
        news_string += f"- {a['title']}\n"
    return news_string

def summarize_with_gemini(text):
    """Direct POST request to Gemini V1 Stable API"""
    # We use '/v1/' here to avoid the 'v1beta' 404 error
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": f"Summarize these tech headlines into a professional daily morning briefing. Focus on new product launches and big tech updates:\n\n{text}"}]
        }]
    }
    
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code != 200:
        return f"AI Summary Error: {response.text}"
    
    result = response.json()
    return result['candidates'][0]['content']['parts'][0]['text']

def send_email(body):
    """Send the final email via Gmail"""
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = f"🚀 Tech Daily: {datetime.now().strftime('%d %b %Y')}"
    msg['From'] = SENDER
    msg['To'] = RECEIVER

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(SENDER, PASSWORD)
        smtp.send_message(msg)

if __name__ == "__main__":
    print("Step 1: Fetching News...")
    raw_news = get_tech_news()
    
    print("Step 2: Summarizing with Gemini V1...")
    summary = summarize_with_gemini(raw_news)
    
    print("Step 3: Sending Email...")
    send_email(summary)
    print("Success! Check your inbox.")
