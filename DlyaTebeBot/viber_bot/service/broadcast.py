import time
import requests
from django.conf import settings

from viber_bot.repo import ViberMessageRepo
from viber_bot.builders import BroadcastCardBuilder


def chunk_list(data, size=300):
    for i in range(0, len(data), size):
        yield data[i:i + size]


def broadcast(text: str, image_url: str | None = None):

    url = "https://chatapi.viber.com/pa/broadcast_message"

    headers = {
        "X-Viber-Auth-Token": settings.VIBER_BOT_TOKEN,
        "Content-Type": "application/json"
    }

    unsubscribe_text = (
        'Не бажаєте отримувати такі повідомлення? '
        'Натисніть кнопку "❌ Відписатися".'
    )


    user_ids = list(ViberMessageRepo.get_user_ids_less_24())

    for batch in chunk_list(user_ids, 300):

        if image_url:

            builder = (
                BroadcastCardBuilder()
                .add_image(image_url)
                .add_text(text, rows=3)
                .add_unsubscribe_button()
                .add_menu_button()
            )

            payload = {
                "broadcast_list": batch,
                "type": "rich_media",
                "min_api_version": 2,
                "rich_media": builder.build()
            }

        else:

            builder = (
                BroadcastCardBuilder()
                .add_text(text, rows=3)
                .add_text(unsubscribe_text, rows=2)
                .add_unsubscribe_button()
                .add_menu_button()
            )

            payload = {
                "broadcast_list": batch,
                "type": "rich_media",
                "min_api_version": 2,
                "rich_media": builder.build()
            }

        response = requests.post(url, json=payload, headers=headers)

        print(response.json())

        time.sleep(0.4)