from loguru import logger

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from ..repo import MessageRepo, TgUserRepo
from ..keyboards.user import get_contact_keyboard, main_menu_keyboard
from ..states import UserStates
from ..utils import send_message

router = Router()
msg_repo = MessageRepo()
tg_user_repo = TgUserRepo()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await send_message(
        message=message,
        message_name="start",
        keyboard=get_contact_keyboard(),
    )

    await state.set_state(UserStates.contact)


@router.message(UserStates.contact)
async def handle_contact(message: Message, state: FSMContext) -> None:
    msg = await msg_repo.get_message_by_name("contact_received")

    try:
        phone_number = message.contact.phone_number
    except AttributeError:
        phone_number = message.text if message.text.startswith("380") else None
    except Exception as e:
        logger.error(f"Error retrieving contact: {e}")
        phone_number = None

    tg_user, created = await tg_user_repo.get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        phone_number=phone_number,
    )

    if created:
        logger.info(f"New user created: {tg_user.first_name}")

    # TODO додати логіку збереження номеру телефону користувача та перевірки чи існує в СРМ

    if phone_number:
        await send_message(
            message=message, 
            message_name="contact_received",
            keyboard=main_menu_keyboard()
        )
    await state.clear()

@router.message(F.text == "Зв'язатися з нами")
async def contact_request_message(message: Message) -> Message:
    await send_message(
        message=message,
        message_name="contact_request",
        keyboard=main_menu_keyboard()
    )

@router.message(F.text == "Instagram, TikTok")
async def social_media_message(message: Message) -> Message:
    await send_message(
        message=message,
        message_name="social_media"
    )