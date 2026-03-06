from typing import Any, Optional
import logging
from datetime import datetime

from django.conf import settings
from viberbot.api.viber_requests import (
    ViberMessageRequest,
    ViberConversationStartedRequest,
)
from viberbot.api.messages import ContactMessage, TextMessage

from bot.api import ApiCRM
from bots_settings.repo import PromoCampaignRepo, MessageRepo
from .services import ViberService
from .repo import ViberUserRepo, ViberMessageRepo
from .fsm import get_state



logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
)

# Ініціалізація сервісу
repo = ViberUserRepo()
promo_repo = PromoCampaignRepo()
msg_repo = MessageRepo()
crm_client = ApiCRM(settings.PHONE_CRM_AUTH, settings.PASSWORD_CRM)
service = ViberService(repo, promo_repo, crm_client, msg_repo)

handlers = []


def viber_handler(
    text: str = None, state: Any = None, request_type=ViberMessageRequest, match: str = "exact"
):
    def decorator(func):
        handlers.append(
            {"type": request_type, "text": text, "state": state, "func": func, "match": match}
        )
        return func
    return decorator


def handle_request(viber_request: Any, viber: Optional[Any] = None) -> None:
    logger.info(viber_request.__dict__)
    user_id = getattr(getattr(viber_request, "sender", None), "id", None)
    if user_id is None:
        user_id = getattr(getattr(viber_request, "user", None), "id", None)
    if user_id is None:
        user_id = getattr(viber_request, "user_id", None)

    text = ""
    action = None

    

    if isinstance(viber_request, ViberMessageRequest):
        text = getattr(viber_request.message, "text", "")
        action = getattr(viber_request.message, "action_body", text)

    logger.info(
        f"user_id={user_id} | time={datetime.now().isoformat()} | action={action} | text={text}"
    )

    # Store incoming message
    if isinstance(viber_request, ViberMessageRequest):
        logger.info(vars(viber_request.message))

        message = viber_request.message
        message_type = getattr(message, "_message_type", "_text")

        text = getattr(message, "text", "")
        media_url = None

        if message_type == "picture":
            media_url = getattr(message, "_media", None)

        user, _ = repo.update_or_create(
            user_id,
            name=viber_request.sender.name,
        )

        ViberMessageRepo.create(
            user=user,
            text=text,
            media_url=media_url,
            is_bot=False,
            timestamp=viber_request.timestamp
        )

    for h in handlers:
        if h["type"] and not isinstance(viber_request, h["type"]):
            continue
        if isinstance(viber_request, ViberMessageRequest):
            message = viber_request.message
            text = getattr(message, "text", "").strip()
            action = getattr(message, "action_body", text)
            if h["text"]:
                if h["match"] == "startswith":
                    if not action.startswith(h["text"]):
                        continue
                else:  # exact
                    if h["text"] != action:
                        continue
            if h["state"] and h["state"] != get_state(user_id):
                continue
        h["func"](viber_request, viber)
        break


@viber_handler(text="hello")
def hello(viber_request: Any, viber: Optional[Any] = None) -> None:
    user_id = viber_request.sender.id
    from .fsm import set_state
    from .keyboards import contact
    set_state(user_id, "contact")
    messages = [
        TextMessage(
            text=msg_repo.get_text("start"),
            keyboard=contact(),
            min_api_version=6,
        )
    ]
    viber.send_messages(user_id, messages)


@viber_handler(text="__CHECK_PRICE__")
def check_price(viber_request: Any, viber: Optional[Any] = None) -> None:
    user_id = viber_request.sender.id
    messages = service.handle_default(user_id)
    viber.send_messages(user_id, messages)


@viber_handler(state="contact")
def handle_contact(viber_request: Any, viber: Optional[Any] = None) -> None:
    user_id = viber_request.sender.id
    phone = ""
    if isinstance(viber_request.message, ContactMessage):
        phone = viber_request.message.contact.phone_number
    elif hasattr(viber_request.message, 'text') and viber_request.message.text.isdigit():
        phone = viber_request.message.text
    else:
        from .keyboards import contact
        messages = [
            TextMessage(
                text=msg_repo.get_text("start"),
                keyboard=contact(),
                min_api_version=6,
            )
        ]
        viber.send_messages(user_id, messages)
        return
    messages = service.handle_contact(user_id, viber_request.sender.name, phone)
    viber.send_messages(user_id, messages)


@viber_handler(request_type=ViberConversationStartedRequest)
def handle_start_request(viber_request: Any, viber: Optional[Any] = None) -> None:
    user_id = viber_request.user.id
    messages = service.handle_start(user_id, viber_request.user.name)
    viber.send_messages(user_id, messages)


@viber_handler(text="my_bonus_card")
def handle_bonus_card(viber_request: Any, viber: Optional[Any] = None) -> None:
    user_id = viber_request.sender.id
    messages = service.handle_bonus_card(user_id)
    viber.send_messages(user_id, messages)


@viber_handler(text="contact_us")
def handle_contact_us(viber_request: Any, viber: Optional[Any] = None) -> None:
    user_id = viber_request.sender.id
    messages = service.handle_contact_us(user_id)
    viber.send_messages(user_id, messages)


@viber_handler(text="social_media")
def handel_social_media(viber_request: Any, viber: Optional[Any] = None) -> None:
    user_id = viber_request.sender.id
    messages = service.handle_social_media(user_id)
    viber.send_messages(user_id, messages)


@viber_handler(text="promo")
def promocampaigns(viber_request: Any, viber: Optional[Any] = None) -> None:
    user_id = viber_request.sender.id
    messages = service.handle_promo(user_id)
    viber.send_messages(user_id, messages)


@viber_handler(text="my_purchaces")
def handle_purchaces(viber_request: Any, viber: Optional[Any] = None) -> None:
    user_id = viber_request.sender.id
    messages = service.handle_purchases(user_id)
    viber.send_messages(user_id, messages)


@viber_handler(match="startswith", text="details_")
def handle_purchase_details(viber_request: Any, viber: Optional[Any] = None) -> None:
    purchase_id = int(viber_request.message.text.split("_")[1])
    user_id = viber_request.sender.id
    messages = service.handle_purchase_detail(user_id, purchase_id)
    viber.send_messages(user_id, messages)


@viber_handler(match="startswith", text="promo_")
def handle_promo_details(viber_request: Any, viber: Optional[Any] = None) -> None:
    promo_id = int(viber_request.message.text.split("_")[1])
    user_id = viber_request.sender.id
    messages = service.handle_promo_details(promo_id, user_id)
    viber.send_messages(user_id, messages)


@viber_handler(request_type=TextMessage)
def answer_to_message(viber_request: Any, viber: Optional[Any] = None) -> None:
    user_id = viber_request.sender.id
    messages = service.handle_default(user_id)
    viber.send_messages(user_id, messages)
