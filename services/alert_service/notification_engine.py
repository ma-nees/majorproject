# services/alert_service/notification_engine.py
import json
import requests
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

class NotificationChannel(Enum):
    CONSOLE = "console"
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"

@dataclass
class Alert:
    """Represents an alert to be sent."""
    title: str
    message: str
    severity: str  # "info", "warning", "critical"
    channel: NotificationChannel
    metadata: Optional[Dict] = None

class NotificationEngine:
    """
    Sends notifications through various channels.
    Reads configuration from a dict (e.g., loaded from config.yaml).
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        config example:
        {
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "alerts@example.com",
                "password": "xxx",
                "from_addr": "alerts@example.com",
                "to_addrs": ["admin@example.com"]
            },
            "slack": {
                "webhook_url": "https://hooks.slack.com/services/xxx"
            },
            "webhook": {
                "url": "https://my-webhook.example.com/alert"
            }
        }
        """
        self.config = config
        self._slack_webhook = config.get("slack", {}).get("webhook_url")
        self._email_config = config.get("email", {})
        self._webhook_url = config.get("webhook", {}).get("url")
    
    async def send_async(self, alert: Alert) -> bool:
        """Send alert asynchronously (recommended for production)."""
        if alert.channel == NotificationChannel.CONSOLE:
            return self._send_console(alert)
        elif alert.channel == NotificationChannel.EMAIL:
            return await self._send_email_async(alert)
        elif alert.channel == NotificationChannel.SLACK:
            return await self._send_slack_async(alert)
        elif alert.channel == NotificationChannel.WEBHOOK:
            return await self._send_webhook_async(alert)
        else:
            logger.error(f"Unknown channel: {alert.channel}")
            return False
    
    def send_sync(self, alert: Alert) -> bool:
        """Synchronous version (for blocking contexts)."""
        if alert.channel == NotificationChannel.CONSOLE:
            return self._send_console(alert)
        elif alert.channel == NotificationChannel.EMAIL:
            return self._send_email_sync(alert)
        elif alert.channel == NotificationChannel.SLACK:
            return self._send_slack_sync(alert)
        elif alert.channel == NotificationChannel.WEBHOOK:
            return self._send_webhook_sync(alert)
        return False
    
    def _send_console(self, alert: Alert) -> bool:
        print(f"\n[ALERT][{alert.severity.upper()}] {alert.title}\n{alert.message}\n")
        return True
    
    async def _send_slack_async(self, alert: Alert) -> bool:
        if not self._slack_webhook:
            logger.warning("Slack webhook not configured")
            return False
        payload = {
            "text": f"*[{alert.severity.upper()}] {alert.title}*\n{alert.message}",
            "attachments": [{"color": self._severity_to_color(alert.severity)}]
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self._slack_webhook, json=payload) as resp:
                    return resp.status == 200
        except Exception as e:
            logger.error(f"Slack send failed: {e}")
            return False
    
    def _send_slack_sync(self, alert: Alert) -> bool:
        if not self._slack_webhook:
            return False
        payload = {"text": f"[{alert.severity}] {alert.title}\n{alert.message}"}
        try:
            r = requests.post(self._slack_webhook, json=payload, timeout=5)
            return r.status_code == 200
        except Exception as e:
            logger.error(f"Slack send failed: {e}")
            return False
    
    async def _send_email_async(self, alert: Alert) -> bool:
        # For async, run sync SMTP in thread pool
        return await asyncio.to_thread(self._send_email_sync, alert)
    
    def _send_email_sync(self, alert: Alert) -> bool:
        if not self._email_config:
            logger.warning("Email not configured")
            return False
        try:
            msg = MIMEMultipart()
            msg['From'] = self._email_config.get('from_addr')
            msg['To'] = ", ".join(self._email_config.get('to_addrs', []))
            msg['Subject'] = f"[{alert.severity.upper()}] {alert.title}"
            msg.attach(MIMEText(alert.message, 'plain'))
            
            with smtplib.SMTP(self._email_config['smtp_server'],
                              self._email_config['smtp_port']) as server:
                server.starttls()
                server.login(self._email_config['username'],
                             self._email_config['password'])
                server.send_message(msg)
            logger.info(f"Email alert sent: {alert.title}")
            return True
        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return False
    
    async def _send_webhook_async(self, alert: Alert) -> bool:
        if not self._webhook_url:
            return False
        payload = {
            "title": alert.title,
            "message": alert.message,
            "severity": alert.severity,
            "timestamp": alert.metadata.get("timestamp") if alert.metadata else None,
            "metadata": alert.metadata
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self._webhook_url, json=payload) as resp:
                    return resp.status == 200
        except Exception as e:
            logger.error(f"Webhook send failed: {e}")
            return False
    
    def _send_webhook_sync(self, alert: Alert) -> bool:
        if not self._webhook_url:
            return False
        payload = {"title": alert.title, "message": alert.message, "severity": alert.severity}
        try:
            r = requests.post(self._webhook_url, json=payload, timeout=5)
            return r.status_code == 200
        except Exception as e:
            logger.error(f"Webhook send failed: {e}")
            return False
    
    @staticmethod
    def _severity_to_color(severity: str) -> str:
        if severity == "critical":
            return "danger"
        elif severity == "warning":
            return "warning"
        else:
            return "good"


# Singleton engine instance
_engine_instance = None

def get_notification_engine(config: Optional[Dict] = None) -> NotificationEngine:
    global _engine_instance
    if _engine_instance is None:
        if config is None:
            # Try to load from default config
            import yaml
            from pathlib import Path
            config_path = Path("config/config.yaml")
            if config_path.exists():
                with open(config_path) as f:
                    full_config = yaml.safe_load(f)
                    config = full_config.get("alert_service", {})
            else:
                config = {}
        _engine_instance = NotificationEngine(config)
    return _engine_instance