import mimetypes

from aiogram import Bot
from aiogram.types import (
    Message,
    FSInputFile,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
    BufferedInputFile,
)
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..models import Message as DbMessage


def get_keyboard_for_message(
    db_message: DbMessage,
) -> ReplyKeyboardMarkup | InlineKeyboardMarkup | None:
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
        InlineKeyboardButton(
            text="⬅️ Повернутися в меню",
            callback_data="main_menu"
        )
    )

    return builder.as_markup()


async def send_message(
    message: Message,
    message_name: str,
    photo: BufferedInputFile = None,
    keyboard: ReplyKeyboardMarkup | InlineKeyboardMarkup = None,
) -> Message:
    db_message = await DbMessage.objects.prefetch_related("buttons").aget(
        name=message_name
    )

    if not keyboard:
        keyboard = get_keyboard_for_message(db_message)

    if photo or db_message.image:
        if not photo:
            mime_type, _ = mimetypes.guess_type(db_message.image.path)
            if mime_type and mime_type.startswith("image/"):

                photo = FSInputFile(db_message.image.path)
                
        msg = await message.answer_photo(
            photo=photo, caption=db_message.text, reply_markup=keyboard
        )
    else:
        msg = await message.answer(text=db_message.text, reply_markup=keyboard)

    return msg


async def edit_message(
    message: Message,
    message_name: str,
    keyboard: ReplyKeyboardMarkup | InlineKeyboardMarkup = None,
) -> Message:
    db_message = await DbMessage.objects.prefetch_related("buttons").aget(
        name=message_name
    )

    if not keyboard:
        keyboard = get_keyboard_for_message(db_message)

    if db_message.image:
        mime_type, _ = mimetypes.guess_type(db_message.image.path)
        if mime_type and mime_type.startswith("image/"):
            photo = FSInputFile(db_message.image.path)
            media = InputMediaPhoto(media=photo, caption=db_message.text)
            msg = await message.edit_media(media=media, reply_markup=keyboard)
            msg = await message.edit_text(text=db_message.text, reply_markup=keyboard)
    else:
        msg = await message.edit_text(text=db_message.text, reply_markup=keyboard)

    return msg


async def edit_message_by_id(
    bot: Bot,
    chat_id: int,
    message_id: int,
    db_message_name: str,
    keyboard: ReplyKeyboardMarkup | InlineKeyboardMarkup = None
) -> Message:
    db_message = await DbMessage.objects.prefetch_related("buttons").aget(name=db_message_name)

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