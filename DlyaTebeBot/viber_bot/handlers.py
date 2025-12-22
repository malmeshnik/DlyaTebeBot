from typing import Any
import logging
from datetime import datetime

from viberbot.api.viber_requests import (
    ViberMessageRequest,
    ViberConversationStartedRequest,
)
from viberbot.api.messages import TextMessage, KeyboardMessage

from .fsm import get_state, set_state, clear_state
from .keyboards import Button, contact, main_menu

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
)

handlers = []


def viber_handler(
    text: str = None, state: Any = None, request_type=ViberMessageRequest
):
    """
    Docstring for viber_handler

    :param text: Text button/command, then filtered
    :type text: str
    :param state: State user, ho use this handler
    :type state: Any
    :param request_type: Request type (ViberMessageRequest, ViberConversationStartedRequest, ...)
    """

    def decorator(func):
        handlers.append(
            {"type": request_type, "text": text, "state": state, "func": func}
        )

        return func

    return decorator


def handle_request(viber_request, viber=None):
    """
    Docstring for handle_request

    :param viber_request: Description
    """

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

    for h in handlers:
        if h["type"] and not isinstance(viber_request, h["type"]):
            continue

        if isinstance(viber_request, ViberMessageRequest):
            message = viber_request.message

            text = ""
            action = None

            if hasattr(message, "text"):
                text = (message.text or "").strip()
                action = getattr(message, "action_body", text)

            elif hasattr(message, "contact"):
                text = message.contact.phone_number
                action = "__CONTACT__"

            user_id = viber_request.sender.id
            user_state = get_state(user_id)

            if h["text"] and h["text"] != action:
                continue

            if h["state"] and h["state"] != user_state:
                continue

        h["func"](viber_request, viber)
        break


def send_text(viber, user_id, text):
    """
    Відправка текстового повідомлення користувачу

    :param viber: обʼєкт viber Api
    :param user_id: ID користувача
    :param text: текст повідомлення
    """
    viber.send_messages(user_id, [TextMessage(text=text)])


@viber_handler(text="hello")
def hello(viber_request, viber=None):
    user_id = viber_request.sender.id
    set_state(user_id, "contact")
    viber.send_messages(
        user_id,
        [
            TextMessage(
                text="Shut up Nigga",
                keyboard=main_menu(),
                min_api_version=3,
            )
        ],
    )


@viber_handler(text="__CHECK_PRICE__")
def check_price(viber_request, viber=None):
    user_id = viber_request.sender.id

    send_text(viber, user_id, "Введи назву товару")


@viber_handler(text="__CONTACT__", state="contact")
def handle_contact(viber_request, viber=None):
    user_id = viber_request.sender.id
    phone = viber_request.message.contact.phone_number

    clear_state(user_id)

    viber.send_messages(
        user_id,
        [
            TextMessage(
                text=f"Дякую! Отримали номер: {phone}",
                keyboard=main_menu(),
                min_api_version=3,
            )
        ],
    )


@viber_handler(request_type=ViberConversationStartedRequest)
def handle_start_request(viber_request, viber=None):
    user_id = viber_request.user.id
    viber.send_messages(
        user_id,
        [
            TextMessage(
                text="Вітаю! Для продовження роботи відправте ваш номер телефону за допомогою кнопки 👇або введіть номер у форматі 380XXXXXXX",
                keyboard=contact(),
                min_api_version=3,
            )
        ],
    )
    set_state(user_id, "contact")


# @viber_handler()
# def answer_to_message(viber_request, viber=None):
#     user_id = viber_request.sender.id
#     viber.send_messages(user_id, [TextMessage(text=viber_request.message.text)])
