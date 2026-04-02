import os
import requests
import google.generativeai as genai
import smtplib
from email.message import EmailMessage
from datetime import datetime
from dotenv import load_dotenv

# Load credentials
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_tech_news():
    """Fetch top tech headlines from the last 24 hours."""
    url = f"https://newsapi.org/v2/top-headlines?category=technology&language=en&apiKey={os.getenv('NEWS_API_KEY')}"
    response = requests.get(url).json()
    
    if response.get("status") != "ok":
        return "Error fetching news."
    
    articles = response.get("articles", [])[:15] # Take top 15 stories
    news_text = ""
    for i, art in enumerate(articles, 1):
        news_text += f"{i}. {art['title']} - {art['description']}\n"
    return news_text

def summarize_news(raw_news):
    """Use Gemini to create a professional summary."""
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    You are a professional tech journalist. Summarize the following news headlines into a clean, 
    bulleted daily briefing. Focus on 'New Launches' and 'Big Tech breakthroughs'. 
    Keep it concise and readable for a 6:00 AM email.
    
    NEWS DATA:
    {raw_news}
    """
    response = model.generate_content(prompt)
    return response.text

def send_email(summary):
    """Send the final summary via Gmail."""
    msg = EmailMessage()
    msg.set_content(summary)
    msg['Subject'] = f"🚀 Tech Briefing: {datetime.now().strftime('%d %b %Y')}"
    msg['From'] = os.getenv("SENDER_EMAIL")
    msg['To'] = os.getenv("RECEIVER_EMAIL")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(os.getenv("SENDER_EMAIL"), os.getenv("EMAIL_PASS"))
        smtp.send_message(msg)

if __name__ == "__main__":
    print("Fetching news...")
    raw_data = get_tech_news()
    print("Summarizing...")
    final_summary = summarize_news(raw_data)
    print("Sending email...")
    send_email(final_summary)
    print("Done!")
