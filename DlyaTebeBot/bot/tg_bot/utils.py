import mimetypes
from typing import Tuple

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    BufferedInputFile,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger

from bot.models import Message as DbMessage
from bot.tg_bot.repo import TgUserRepo


def get_keyboard_for_message(
    db_message: DbMessage,
) -> ReplyKeyboardMarkup | InlineKeyboardMarkup | None:
    """Creates a keyboard markup for a message."""
    buttons = list(db_message.buttons.all())
    builder = InlineKeyboardBuilder()

    if buttons:
        for button in db_message.buttons.all():
            builder.add(InlineKeyboardButton(text=button.text, url=button.url))

    builder.row(
        InlineKeyboardButton(text="⬅️ Повернутися в меню", callback_data="main_menu")
    )

    return builder.as_markup()


async def _prepare_message(
    message_name: str, from_user_name: str, bonus: int = None
) -> Tuple[str, InlineKeyboardMarkup | ReplyKeyboardMarkup, DbMessage]:
    """Prepares a message for sending."""
    db_message = await DbMessage.objects.prefetch_related("buttons").aget(
        name=message_name
    )
    message_text = db_message.text.format(bonus=bonus, name=from_user_name)
    keyboard = get_keyboard_for_message(db_message)
    return message_text, keyboard, db_message


async def send_message(
    message: Message,
    message_name: str,
    user_repo: TgUserRepo = None,
    photo: BufferedInputFile = None,
    keyboard: ReplyKeyboardMarkup | InlineKeyboardMarkup = None,
    bonus: int = None,
) -> Message:
    """Sends a message to the user."""
    message_text, default_keyboard, db_message = await _prepare_message(
        message_name, message.from_user.first_name, bonus
    )
    keyboard = keyboard or default_keyboard

    if photo or db_message.image:
        if not photo:
            mime_type, _ = mimetypes.guess_type(db_message.image.path)
            if mime_type and mime_type.startswith("image/"):
                photo = FSInputFile(db_message.image.path)

        msg = await message.answer_photo(
            photo=photo, caption=message_text, reply_markup=keyboard
        )
    else:
        msg = await message.answer(text=message_text, reply_markup=keyboard)

    if message_name == "start":
        user_id = message.chat.id
        logger.info(
            f"Saving message with main menu for user: {user_id}, message_id: {msg.message_id}"
        )
        await user_repo.save_main_message(user_id, msg.message_id)

    return msg


async def edit_message(
    message: Message,
    message_name: str,
    user_repo: TgUserRepo,
    keyboard: ReplyKeyboardMarkup | InlineKeyboardMarkup = None,
    bonus: int = None,
) -> Message:
    """Edits an existing message."""
    logger.info(f"Editing message with name: {message_name}")
    message_text, default_keyboard, db_message = await _prepare_message(
        message_name, message.chat.first_name, bonus
    )
    keyboard = keyboard or default_keyboard

    if db_message.image:
        mime_type, _ = mimetypes.guess_type(db_message.image.path)
        if mime_type and mime_type.startswith("image/"):
            photo = FSInputFile(db_message.image.path)
            media = InputMediaPhoto(media=photo, caption=message_text)
            msg = await message.edit_media(media=media, reply_markup=keyboard)
        else:
            msg = await message.edit_text(text=message_text, reply_markup=keyboard)
    else:
        try:
            msg = await message.edit_text(text=message_text, reply_markup=keyboard)
        except TelegramBadRequest:
            await message.delete()
            msg = await message.answer(text=message_text, reply_markup=keyboard)

    if message_name == "contact_received":
        user_id = message.chat.id
        logger.info(
            f"Saving message with main menu for user: {user_id}, message_id: {msg.message_id}"
        )
        await user_repo.save_main_message(user_id, msg.message_id)

    return msg


async def edit_message_by_id(
    bot: Bot,
    chat_id: int,
    message_id: int,
    db_message_name: str,
    keyboard: ReplyKeyboardMarkup | InlineKeyboardMarkup = None,
) -> Message:
    """Edits an existing message by its ID."""
    db_message = await DbMessage.objects.prefetch_related("buttons").aget(
        name=db_message_name
    )
    keyboard = keyboard or get_keyboard_for_message(db_message)

    if db_message.image:
        mime, _ = mimetypes.guess_type(db_message.image.path)
        if mime and mime.startswith("image/"):
            media = InputMediaPhoto(
                media=FSInputFile(db_message.image.path),
                caption=db_message.text,
            )
            try:
                return await bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=media,
                    reply_markup=keyboard,
                )
            except TelegramBadRequest:
                return await bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=message_id,
                    caption=db_message.text,
                    reply_markup=keyboard,
                )

    try:
        return await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=db_message.text,
            reply_markup=keyboard,
        )
    except TelegramBadRequest:
        return None
