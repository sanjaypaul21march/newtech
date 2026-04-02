import os
import requests
import json
import smtplib
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# We force everything to UTF-8 strings immediately
NEWS_KEY = str(os.getenv("NEWS_API_KEY", "")).strip()
GEMINI_KEY = str(os.getenv("GEMINI_API_KEY", "")).strip()
SENDER = str(os.getenv("SENDER_EMAIL", "")).strip()
PASSWORD = str(os.getenv("EMAIL_PASS", "")).strip()
RECEIVER = str(os.getenv("RECEIVER_EMAIL", "")).strip()

def get_tech_news():
    url = f"https://newsapi.org/v2/top-headlines?category=technology&language=en&apiKey={NEWS_KEY}"
    try:
        r = requests.get(url)
        data = r.json()
        articles = data.get("articles", [])[:10]
        return "\n".join([f"- {a.get('title', 'No News')}" for a in articles])
    except:
        return "No news fetched."

def summarize_with_gemini(text):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {"contents": [{"parts": [{"text": f"Summarize this news:\n\n{text}"}]}]}
    try:
        r = requests.post(url, json=payload)
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return text # Fallback to raw news if AI fails

def send_email(content):
    subject = f"Tech News {datetime.now().strftime('%d %b')}"
    # Use the most basic manual format to avoid the email library entirely
    raw_message = f"Subject: {subject}\n\n{content}"

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        # We manually encode the strings to bytes only at the moment of sending
        # This prevents the 'concatenate' error during the login phase
        server.login(SENDER, PASSWORD)
        server.sendmail(SENDER, RECEIVER, raw_message.encode("utf-8"))
        server.quit()
        print("Success: Email sent!")
    except Exception as e:
        print(f"SMTP Error: {str(e)}")

if __name__ == "__main__":
    news = get_tech_news()
    summary = summarize_with_gemini(news)
    send_email(summary)
