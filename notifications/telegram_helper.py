import requests
from django.conf import settings


def send_message(text):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": settings.TELEGRAM_CHAT_ID, "text": text}
    requests.post(url, data=data)
