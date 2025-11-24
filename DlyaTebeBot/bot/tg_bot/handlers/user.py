from aiogram import F, Router
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from loguru import logger

from bot.tg_bot.keyboards.user import get_contact_keyboard, main_menu_keyboard
from bot.tg_bot.repo import MessageRepo, TgUserRepo
from bot.tg_bot.states import UserStates
from bot.tg_bot.utils import send_message

router = Router()
msg_repo = MessageRepo()
tg_user_repo = TgUserRepo()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    """Handles the /start command.

    If the user is new, it prompts them to share their contact information.
    Otherwise, it displays the main menu.

    Args:
        message: The incoming message object.
        state: The FSM context for managing user states.
    """
    user = await tg_user_repo.get_user(message.from_user.id)

    if not user:
        await send_message(
            message=message,
            message_name="start",
            user_repo=tg_user_repo,
            keyboard=get_contact_keyboard(),
        )

        await state.set_state(UserStates.contact)
        return

    await send_message(
        message=message,
        message_name="contact_received",
        user_repo=tg_user_repo,
        keyboard=main_menu_keyboard(),
    )


@router.message(UserStates.contact, F.contact)
async def handle_contact(message: Message, state: FSMContext) -> None:
    """Handles the user's contact information.

    It extracts the phone number from the message, creates a new user in the database,
    and displays the main menu.

    Args:
        message: The incoming message object.
        state: The FSM context for managing user states.
    """
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

    if phone_number:
        msg = await message.answer("deletecontact", reply_markup=ReplyKeyboardRemove())
        await msg.delete()
        await send_message(
            message=message,
            message_name="contact_received",
            user_repo=tg_user_repo,
            keyboard=main_menu_keyboard(),
        )
    await state.clear()
