import requests
from typing import Optional
import config


class WebhookSender:
    def __init__(self):
        self.telegram_config = config.WEBHOOK_CONFIG.get("telegram", {})
        self.discord_config = config.WEBHOOK_CONFIG.get("discord", {})

    def send_telegram(self, message: str, chat_id: str = None) -> bool:
        if not self.telegram_config.get("enabled"):
            return False
        
        token = self.telegram_config.get("bot_token")
        chat = chat_id or self.telegram_config.get("chat_id")
        
        if not token or not chat:
            return False
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            "chat_id": chat,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def send_discord(self, message: str, username: str = "Reply Bot") -> bool:
        if not self.discord_config.get("enabled"):
            return False
        
        webhook_url = self.discord_config.get("webhook_url")
        
        if not webhook_url:
            return False
        
        data = {
            "content": message,
            "username": username
        }
        
        try:
            response = requests.post(webhook_url, json=data, timeout=10)
            return response.status_code in [200, 204]
        except Exception:
            return False

    def broadcast(self, message: str, platform: str = "all") -> dict:
        results = {}
        
        if platform in ["telegram", "all"]:
            results["telegram"] = self.send_telegram(message)
        
        if platform in ["discord", "all"]:
            results["discord"] = self.send_discord(message)
        
        return results
