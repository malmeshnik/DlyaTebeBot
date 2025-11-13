import mimetypes
import json
from io import BytesIO
from loguru import logger

import qrcode
from aiogram import Bot
from aiogram.types import (
    Message,
    FSInputFile,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
    BufferedInputFile,
    BufferedInputFile,
)
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..models import Message as DbMessage
from .repo import TgUserRepo


def get_keyboard_for_message(
    db_message: DbMessage,
) -> ReplyKeyboardMarkup | InlineKeyboardMarkup | None:
    """Creates a keyboard markup for a message.

    Args:
        db_message: The message object from the database.

    Returns:
        An `InlineKeyboardMarkup` object if the message has buttons, otherwise `None`.
    """
    buttons = list(db_message.buttons.all())
    builder = InlineKeyboardBuilder()

    if buttons:

        for button in db_message.buttons.all():
            builder.add(
                InlineKeyboardButton(
                    text=button.text,
                    url=button.url,
                )
            )

    builder.row(
        InlineKeyboardButton(text="⬅️ Повернутися в меню", callback_data="main_menu")
    )

    return builder.as_markup()


async def send_message(
    message: Message,
    message_name: str,
    user_repo: TgUserRepo = None,
    photo: BufferedInputFile = None,
    keyboard: ReplyKeyboardMarkup | InlineKeyboardMarkup = None,
    bonus: int = None,
) -> Message:
    """Sends a message to the user.

    Args:
        message: The incoming message object.
        message_name: The name of the message to send.
        user_repo: The user repository for database operations.
        photo: The photo to send with the message.
        keyboard: The keyboard markup for the message.
        bonus: The user's bonus points.

    Returns:
        The sent `Message` object.
    """
    db_message = await DbMessage.objects.prefetch_related("buttons").aget(
        name=message_name
    )
    message_text = db_message.text.format(
        bonus=bonus, name=message.from_user.first_name
    )

    if not keyboard:
        keyboard = get_keyboard_for_message(db_message)

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
    """Edits an existing message.

    Args:
        message: The message object to edit.
        message_name: The name of the new message content.
        user_repo: The user repository for database operations.
        keyboard: The new keyboard markup for the message.
        bonus: The user's bonus points.

    Returns:
        The edited `Message` object.
    """
    logger.info(f"Editing message with name: {message_name}")
    db_message = await DbMessage.objects.prefetch_related("buttons").aget(
        name=message_name
    )
    message_text = db_message.text.format(bonus=bonus, name=message.chat.first_name)

    if not keyboard:
        keyboard = get_keyboard_for_message(db_message)

    if db_message.image:
        mime_type, _ = mimetypes.guess_type(db_message.image.path)
        if mime_type and mime_type.startswith("image/"):
            photo = FSInputFile(db_message.image.path)
            media = InputMediaPhoto(media=photo, caption=message_text)
            msg = await message.edit_media(media=media, reply_markup=keyboard)
            msg = await message.edit_text(text=message_text, reply_markup=keyboard)
    else:
        try:
            msg = await message.edit_text(text=message_text, reply_markup=keyboard)
        except:
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
    """Edits an existing message by its ID.

    Args:
        bot: The bot instance.
        chat_id: The ID of the chat where the message is located.
        message_id: The ID of the message to edit.
        db_message_name: The name of the new message content from the database.
        keyboard: The new keyboard markup for the message.

    Returns:
        The edited `Message` object, or `None` if an error occurred.
    """
    db_message = await DbMessage.objects.prefetch_related("buttons").aget(
        name=db_message_name
    )

    if keyboard is None:
        keyboard = get_keyboard_for_message(db_message)

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


def generate_qr_code(phone: str) -> BufferedInputFile:
    """Generates a QR code containing the user's phone number.

    Args:
        phone: The user's phone number.

    Returns:
        A `BufferedInputFile` object representing the QR code image.
    """
    data = {"phone": phone}
    data_text = json.dumps(data, ensure_ascii=False)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=8,
        border=2,
    )

    qr.add_data(data_text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buf = BytesIO()
    img.save(buf, format="PNG")
    photo = BufferedInputFile(buf.getvalue(), filename="bonus_qr.png")

    return photo
