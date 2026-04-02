import os
import requests
import json
import smtplib
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def get_tech_news():
    url = f"https://newsapi.org/v2/top-headlines?category=technology&language=en&apiKey={os.getenv('NEWS_API_KEY')}"
    try:
        data = requests.get(url).json()
        titles = [f"- {a['title']}" for a in data.get('articles', [])[:10]]
        return "\n".join(titles)
    except:
        return "No news found today."

def summarize_with_gemini(text):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={os.getenv('GEMINI_API_KEY')}"
    payload = {"contents": [{"parts": [{"text": f"Summarize this:\n\n{text}"}]}]}
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    return "AI Summary failed."

def send_email(content):
    sender = str(os.getenv("SENDER_EMAIL")).strip()
    password = str(os.getenv("EMAIL_PASS")).strip()
    receiver = str(os.getenv("RECEIVER_EMAIL")).strip()
    subject = f"Tech Daily {datetime.now().strftime('%d %b')}"
    
    # We build the raw email string manually to avoid library errors
    email_text = f"Subject: {subject}\n\n{content}"

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, email_text.encode("utf-8"))

if __name__ == "__main__":
    print("Running...")
    news = get_tech_news()
    summary = summarize_with_gemini(news)
    send_email(summary)
    print("Done!")
