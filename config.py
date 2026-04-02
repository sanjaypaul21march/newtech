"""
config.py — Tech Briefing Agent Configuration
Edit this file to set your API keys, topics, and delivery preferences.
"""

import os


class Config:
    # ── Anthropic ──────────────────────────────────────────────────────────────
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "YOUR_ANTHROPIC_API_KEY")

    # ── Topics to cover ────────────────────────────────────────────────────────
    # Add or remove topics freely
    topics: list[str] = [
        "🤖 AI & Machine Learning (models, frameworks, research)",
        "🌐 Web Development (frameworks, browser APIs, tooling)",
        "☁️  Cloud & DevOps (AWS, GCP, Azure, containers, CI/CD)",
        "🔐 Cybersecurity (vulnerabilities, patches, best practices)",
        "📦 Open Source (notable releases, project updates)",
    ]

    # ── Email Delivery ─────────────────────────────────────────────────────────
    email_enabled: bool = os.getenv("EMAIL_ENABLED", "false").lower() == "true"

    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "465"))          # 465 = SSL

    email_sender: str = os.getenv("EMAIL_SENDER", "you@gmail.com")
    email_password: str = os.getenv("EMAIL_PASSWORD", "your_app_password")  # Gmail App Password

    # Comma-separated list of recipients
    _recipients_raw: str = os.getenv("EMAIL_RECIPIENTS", "you@gmail.com")
    email_recipients: list[str] = [
        r.strip() for r in _recipients_raw.split(",") if r.strip()
    ]

    # ── Slack Delivery ─────────────────────────────────────────────────────────
    slack_enabled: bool = os.getenv("SLACK_ENABLED", "false").lower() == "true"
    slack_webhook_url: str = os.getenv(
        "SLACK_WEBHOOK_URL",
        "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    )

    # ── Validation ─────────────────────────────────────────────────────────────
    def validate(self) -> None:
        if self.anthropic_api_key == "YOUR_ANTHROPIC_API_KEY":
            raise ValueError(
                "❌ Set ANTHROPIC_API_KEY in your .env file or environment variables."
            )
        if self.email_enabled and self.email_password == "your_app_password":
            raise ValueError(
                "❌ Email is enabled but EMAIL_PASSWORD is not set. "
                "Create a Gmail App Password at https://myaccount.google.com/apppasswords"
            )
        if self.slack_enabled and "YOUR/WEBHOOK" in self.slack_webhook_url:
            raise ValueError(
                "❌ Slack is enabled but SLACK_WEBHOOK_URL is not set. "
                "Create one at https://api.slack.com/messaging/webhooks"
            )
