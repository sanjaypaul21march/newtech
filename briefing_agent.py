#!/usr/bin/env python3
"""
Tech Briefing Agent
Fetches the latest tech updates using Claude + Web Search
and delivers them via Email and/or Slack at 6 AM IST daily.
"""

import anthropic
import smtplib
import json
import os
import sys
import requests
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from zoneinfo import ZoneInfo
from config import Config


# ── Prompt ────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a senior tech analyst delivering a sharp morning briefing.
For each topic, find the most important news or updates from the last 24-48 hours.

Format your response in clean sections like this:

━━━ 🤖 AI & MACHINE LEARNING ━━━
**[Headline]**
Summary in 2 sentences. Why it matters to developers/engineers.

━━━ 🌐 WEB DEVELOPMENT ━━━
...

End with:
━━━ 💡 TODAY'S INSIGHT ━━━
One concise, actionable trend or tip for engineers today.

Be specific — include real project names, version numbers, companies, and links where possible.
Prioritize genuine signal over hype."""


def build_user_prompt(topics: list[str], ist_time: str) -> str:
    topic_list = "\n".join(f"- {t}" for t in topics)
    return f"""Today is {ist_time} IST. Please search the web and deliver a crisp morning tech briefing covering:

{topic_list}

For each topic, find the 1-2 most impactful updates from the last 24-48 hours. Be concise and developer-focused."""


# ── Claude API ────────────────────────────────────────────────────────────────

def fetch_briefing(api_key: str, topics: list[str], ist_time: str) -> str:
    """Call Claude with web search and return the briefing text."""
    client = anthropic.Anthropic(api_key=api_key)

    print("🔍 Querying Claude with web search...")
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[
            {
                "role": "user",
                "content": build_user_prompt(topics, ist_time),
            }
        ],
    )

    # Extract all text blocks (web search may produce multiple blocks)
    text_parts = [
        block.text for block in response.content if block.type == "text"
    ]
    briefing = "\n\n".join(text_parts).strip()

    if not briefing:
        raise ValueError("Claude returned an empty response.")

    print(f"✅ Briefing fetched ({len(briefing)} chars)")
    return briefing


# ── Email Delivery ────────────────────────────────────────────────────────────

def briefing_to_html(briefing: str, ist_time: str) -> str:
    """Convert plain-text briefing to a clean HTML email."""
    lines = briefing.splitlines()
    html_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            html_lines.append("<br>")
        elif stripped.startswith("━━━") and stripped.endswith("━━━"):
            title = stripped.replace("━━━", "").strip()
            html_lines.append(
                f'<h2 style="color:#1a1a2e;border-bottom:2px solid #a8ff78;'
                f'padding-bottom:4px;margin-top:28px;">{title}</h2>'
            )
        elif stripped.startswith("**") and stripped.endswith("**"):
            content = stripped[2:-2]
            html_lines.append(
                f'<p style="font-weight:700;color:#0d1117;margin:12px 0 4px;">{content}</p>'
            )
        else:
            # inline bold
            import re
            formatted = re.sub(
                r"\*\*(.+?)\*\*",
                r'<strong>\1</strong>',
                stripped
            )
            html_lines.append(f'<p style="margin:4px 0;color:#333;">{formatted}</p>')

    body = "\n".join(html_lines)

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:'Segoe UI',Arial,sans-serif;max-width:640px;
             margin:0 auto;padding:24px;background:#f9f9fb;">
  <div style="background:#0d1117;border-radius:10px;padding:24px 28px;margin-bottom:24px;">
    <p style="color:#555;font-size:11px;letter-spacing:3px;margin:0 0 6px;">
      DAILY TECH BRIEFING
    </p>
    <h1 style="color:#fff;margin:0;font-size:26px;">
      Morning Update <span style="color:#a8ff78;">⚡</span>
    </h1>
    <p style="color:#888;font-size:13px;margin:8px 0 0;">{ist_time} IST</p>
  </div>
  <div style="background:#fff;border-radius:10px;padding:24px 28px;
              box-shadow:0 2px 12px rgba(0,0,0,0.06);">
    {body}
  </div>
  <p style="text-align:center;color:#bbb;font-size:11px;margin-top:20px;">
    Powered by Claude + Web Search · Automated Tech Briefing Agent
  </p>
</body>
</html>"""


def send_email(briefing: str, ist_time: str, cfg: Config) -> None:
    """Send the briefing as an HTML email."""
    if not cfg.email_enabled:
        print("📧 Email delivery disabled — skipping.")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"⚡ Tech Briefing — {ist_time} IST"
    msg["From"] = cfg.email_sender
    msg["To"] = ", ".join(cfg.email_recipients)

    # Plain text fallback
    msg.attach(MIMEText(briefing, "plain"))
    # Rich HTML version
    msg.attach(MIMEText(briefing_to_html(briefing, ist_time), "html"))

    print(f"📧 Sending email to {cfg.email_recipients}...")
    with smtplib.SMTP_SSL(cfg.smtp_host, cfg.smtp_port) as server:
        server.login(cfg.email_sender, cfg.email_password)
        server.sendmail(cfg.email_sender, cfg.email_recipients, msg.as_string())
    print("✅ Email sent!")


# ── Slack Delivery ────────────────────────────────────────────────────────────

def send_slack(briefing: str, ist_time: str, cfg: Config) -> None:
    """Post the briefing to a Slack channel via webhook."""
    if not cfg.slack_enabled:
        print("💬 Slack delivery disabled — skipping.")
        return

    # Truncate for Slack's 3000-char block limit
    MAX = 2900
    chunks = [briefing[i : i + MAX] for i in range(0, len(briefing), MAX)]

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"⚡ Tech Briefing — {ist_time} IST"},
        }
    ]
    for chunk in chunks:
        blocks.append(
            {"type": "section", "text": {"type": "mrkdwn", "text": chunk}}
        )
    blocks.append({"type": "divider"})
    blocks.append(
        {
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": "_Powered by Claude + Web Search_"}
            ],
        }
    )

    payload = {"blocks": blocks}
    print("💬 Posting to Slack...")
    resp = requests.post(cfg.slack_webhook_url, json=payload, timeout=15)
    resp.raise_for_status()
    print("✅ Slack message sent!")


# ── Save to file ──────────────────────────────────────────────────────────────

def save_to_file(briefing: str, ist_time: str) -> None:
    """Save briefing to a timestamped text file in ./briefings/"""
    os.makedirs("briefings", exist_ok=True)
    safe_time = ist_time.replace(":", "-").replace(" ", "_")
    path = f"briefings/briefing_{safe_time}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"TECH BRIEFING — {ist_time} IST\n")
        f.write("=" * 60 + "\n\n")
        f.write(briefing)
    print(f"💾 Saved to {path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    cfg = Config()
    cfg.validate()

    # Current time in IST
    ist = ZoneInfo("Asia/Kolkata")
    now_ist = datetime.now(ist)
    ist_time = now_ist.strftime("%A, %d %B %Y %H:%M")

    print(f"\n{'='*55}")
    print(f"  TECH BRIEFING AGENT  |  {ist_time} IST")
    print(f"{'='*55}\n")

    # 1. Fetch briefing from Claude
    briefing = fetch_briefing(cfg.anthropic_api_key, cfg.topics, ist_time)

    # 2. Save locally
    save_to_file(briefing, ist_time)

    # 3. Deliver
    send_email(briefing, ist_time, cfg)
    send_slack(briefing, ist_time, cfg)

    print("\n🎉 Done! Briefing delivered successfully.\n")


if __name__ == "__main__":
    main()
