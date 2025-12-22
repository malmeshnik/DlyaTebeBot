import json

import requests
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Set Viber webhook for this Django project"

    def handle(self, *args, **options):
        base_url = settings.VIBER_WEBHOOK_BASE_URL.rstrip("/")
        path = settings.VIBER_WEBHOOK_PATH  # типу "/viber/webhook/"
        url = base_url + path

        payload = {
            "url": url,
            "event_types": [
                "delivered",
                "seen",
                "failed",
                "subscribed",
                "unsubscribed",
                "conversation_started",
            ],
        }

        headers = {
            "X-Viber-Auth-Token": settings.VIBER_BOT_TOKEN,
            "Content-Type": "application/json",
        }

        resp = requests.post(
            "https://chatapi.viber.com/pa/set_webhook",
            data=json.dumps(payload),
            headers=headers,
            timeout=10,
        )

        self.stdout.write(self.style.NOTICE(f"Request sent to set webhook: {url}"))
        self.stdout.write(self.style.SUCCESS(f"Status code: {resp.status_code}"))
        self.stdout.write(self.style.SUCCESS(f"Response: {resp.text}"))
