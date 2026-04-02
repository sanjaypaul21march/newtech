import os
import requests
import json
import smtplib
from datetime import datetime
from dotenv import load_dotenv

# 1. Load and FORCE every secret to be a clean string immediately
load_dotenv()
NEWS_KEY = str(os.getenv("NEWS_API_KEY", "")).strip()
GEMINI_KEY = str(os.getenv("GEMINI_API_KEY", "")).strip()
SENDER = str(os.getenv("SENDER_EMAIL", "")).strip()
PASSWORD = str(os.getenv("EMAIL_PASS", "")).strip()
RECEIVER = str(os.getenv("RECEIVER_EMAIL", "")).strip()

def get_tech_news():
    """Fetch headlines"""
    url = f"https://newsapi.org/v2/top-headlines?category=technology&language=en&apiKey={NEWS_KEY}"
    try:
        r = requests.get(url)
        data = r.json()
        articles = data.get("articles", [])[:10]
        return "\n".join([f"- {a.get('title', 'No Title')}" for a in articles])
    except:
        return "No news found."

def summarize_with_gemini(text):
    """Direct V1 API call to avoid library issues"""
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {
        "contents": [{"parts": [{"text": f"Summarize these headlines for a daily email:\n\n{text}"}]}]
    }
    try:
        r = requests.post(url, json=payload)
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return f"AI Summary failed. Raw news: {text[:100]}"

def send_email(content):
    """The most basic SMTP method to avoid the 'bytes' error"""
    subject = f"Tech Daily: {datetime.now().strftime('%d %b %Y')}"
    
    # We manually build the raw message string
    # This avoids the 'EmailMessage' library which is causing your crash
    message = f"From: {SENDER}\nTo: {RECEIVER}\nSubject: {subject}\n\n{content}"

    try:
        # Use a context manager for the connection
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            # We login using the stripped strings
            server.login(SENDER, PASSWORD)
            # We encode the entire message at once to send it safely
            server.sendmail(SENDER, RECEIVER, message.encode("utf-8"))
            print("Email sent successfully!")
    except Exception as e:
        print(f"SMTP Error: {str(e)}")

if __name__ == "__main__":
    print("Starting process...")
    news = get_tech_news()
    print("News fetched. Summarizing...")
    summary = summarize_with_gemini(news)
    print("Summary ready. Sending email...")
    send_email(summary)
    print("Workflow complete.")
