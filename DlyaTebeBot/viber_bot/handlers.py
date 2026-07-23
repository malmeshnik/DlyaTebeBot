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
from bot.models import TgUser
from bots_settings.repo import PromoCampaignRepo, MessageRepo
from .services import ViberService
from .repo import ViberUserRepo, ViberMessageRepo
from .fsm import get_state, set_state



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


def _notify_viber_admins(user, text, media_url, viber):
    """Сповіщає всіх Telegram адмінів про нове повідомлення від Viber користувача"""

    # Отримуємо адмінів з Telegram (оскільки в Viber немає is_admin поля)
    from aiogram import Bot
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from asgiref.sync import async_to_sync

    admin_users = list(TgUser.objects.filter(is_admin=True))

    if not admin_users:
        return

    # Формуємо текст сповіщення
    user_name = user.name or f"ID: {user.viber_id}"
    message_preview = ""

    if text:
        message_preview = text[:100] + ("..." if len(text) > 100 else "")
    elif media_url:
        message_preview = "🖼 Зображення"

    notification_text = (
        f"💬 <b>Нове Viber повідомлення</b>\n\n"
        f"👤 <b>Від:</b> {user_name}\n"
        f"🆔 <b>Viber ID:</b> <code>{user.viber_id}</code>\n"
        f"📝 <b>Повідомлення:</b> {message_preview}"
    )

    # Створюємо кнопку з посиланням на чат
    admin_chat_url = f"{settings.ADMIN_URL}/viber_bot/viberuser/chat/{user.id}/"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Відкрити чат", url=admin_chat_url)]
    ])

    # Відправляємо сповіщення всім адмінам через Telegram
    async def send_notifications():
        async with Bot(settings.BOT_TOKEN) as bot:
            for admin in admin_users:
                try:
                    await bot.send_message(
                        chat_id=admin.telegram_id,
                        text=notification_text,
                        parse_mode="HTML",
                        reply_markup=keyboard
                    )
                except Exception as e:
                    logger.error(f"Failed to notify admin {admin.telegram_id}: {e}")

    async_to_sync(send_notifications)()


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
        action = getattr(message, "action_body", text)
        media_url = None

        if message_type == "picture":
            media_url = getattr(message, "_media", None)

        user, _ = repo.update_or_create(
            user_id,
            name=viber_request.sender.name,
        )

        # Зберігаємо тільки реальні повідомлення від користувачів
        # Пропускаємо натискання на кнопки меню та службові дії
        is_menu_action = action in [
            "CHECK_PRICE", "__CHECK_PRICE__", "METRO_CARD", "PROMO",
            "my_bonus_card", "contact_us", "social_media", "promo",
            "my_purchaces", "show_menu", "unsubscribe", "hello"
        ]
        is_details_action = action.startswith("details_") or action.startswith("promo_")

        # Зберігаємо тільки якщо це текст (не дія) або медіа
        should_save = (text and not is_menu_action and not is_details_action) or media_url

        if should_save:
            ViberMessageRepo.create(
                user=user,
                text=text,
                media_url=media_url,
                is_bot=False,
                timestamp=viber_request.timestamp
            )

            # Сповіщення адмінів про нове повідомлення
            _notify_viber_admins(user, text, media_url, viber)

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
            current_state = get_state(user_id)
            if h["state"] and current_state != h["state"]:
                if not (
                    isinstance(current_state, str)
                    and current_state.startswith(f"{h['state']}:")
                ):
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
            text=msg_repo.get_viber_text("start"),
            keyboard=contact(),
            min_api_version=6,
        )
    ]
    viber.send_messages(user_id, messages)

# @viber_handler()
# def handle_contact_global(viber_request, viber=None):
#     logger.info(f"Handling contact_global for user_id={viber_request.sender.id}")
#     if not isinstance(viber_request.message, ContactMessage):
#         return

#     user_id = viber_request.sender.id
#     clear_state(user_id)

#     phone = viber_request.message.contact.phone_number

#     messages = service.handle_contact(
#         user_id,
#         viber_request.sender.name,
#         phone
#     )

#     viber.send_messages(user_id, messages)


@viber_handler(text="__CHECK_PRICE__")
def check_price(viber_request: Any, viber: Optional[Any] = None) -> None:
    user_id = viber_request.sender.id
    messages = service.handle_default(user_id)
    viber.send_messages(user_id, messages)


@viber_handler(state="contact")
def handle_contact(viber_request: Any, viber: Optional[Any] = None) -> None:
    logger.info(f"Handling contact for user_id={viber_request.sender.id}")
    
    user_id = viber_request.sender.id
    phone = ""
    if isinstance(viber_request.message, ContactMessage):
        phone = viber_request.message.contact.phone_number
    elif hasattr(viber_request.message, 'text') and viber_request.message.text.isdigit():
        phone = viber_request.message.text
    else:
        from .keyboards import contact
        set_state(user_id, "contact")
        messages = [
            TextMessage(
                text=msg_repo.get_viber_text("start"),
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
    context = getattr(viber_request, "context", None) or ""

    logger.info(
        f"Viber conversation_started | user_id={user_id} | context={context!r}"
    )

    messages = service.handle_start(user_id, viber_request.user.name, context=context)
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

@viber_handler(text="show_menu")
def handle_show_menu(viber_request: Any, viber: Optional[Any] = None) -> None:
    user_id = viber_request.sender.id
    messages = service.handle_default(user_id)
    viber.send_messages(user_id, messages)

@viber_handler(text="unsubscribe")
def handle_unsubscribe(viber_request: Any, viber: Optional[Any] = None) -> None:
    user_id = viber_request.sender.id
    messages = service.handle_unsubscribe(user_id)
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
    logger.info(f"OUTGOING MESSAGES: {messages}")
    viber.send_messages(user_id, messages)