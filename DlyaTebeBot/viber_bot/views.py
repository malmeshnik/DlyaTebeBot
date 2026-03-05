import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import TextMessage
from viberbot.api.messages import KeyboardMessage

from .handlers import handle_request

viber = Api(
    BotConfiguration(
        name="DLYATEBE",
        avatar=None,
        auth_token=settings.VIBER_BOT_TOKEN
    )
)

def main_menu():
    keyboard = {
        "Type": "keyboard",
        "DefaultHeight": False,
        "BgColor": "#FFFFFF",
        "Buttons": [
            {
                "Columns": 6,
                "Rows": 2,
                "Text": "🔍 Перевірити ціну",
                "ActionType": "reply",
                "ActionBody": "CHECK_PRICE",
                "BgColor": "#0A5ED7",
                "TextColor": "#FFFFFF"
            },
            {
                "Columns": 3,
                "Rows": 2,
                "Text": "💳 Картка METRO",
                "ActionType": "reply",
                "ActionBody": "METRO_CARD",
                "BgColor": "#0A5ED7",
                "TextColor": "#FFFFFF"
            },
            {
                "Columns": 3,
                "Rows": 2,
                "Text": "🔥 Акції",
                "ActionType": "reply",
                "ActionBody": "PROMO",
                "BgColor": "#0A5ED7",
                "TextColor": "#FFFFFF"
            }
        ]
    }

    return KeyboardMessage(
        keyboard=keyboard,
        min_api_version=6
    )




logger = logging.getLogger(__name__)


@csrf_exempt
def viber_webhook(request):
    if request.method != "POST":
        return HttpResponse(status=405)

    # Verify signature
    signature = request.META.get("HTTP_X_VIBER_CONTENT_SIGNATURE")
    if not viber.verify_signature(request.body, signature):
        return HttpResponse(status=403)

    viber_request = viber.parse_request(request.body)
    handle_request(viber_request, viber)

    return HttpResponse(status=200)