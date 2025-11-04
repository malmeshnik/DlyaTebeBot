import mimetypes

from aiogram.types import (
    Message,
    FSInputFile,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..models import Message as DbMessage


def get_keyboard_for_message(
    db_message: DbMessage,
) -> ReplyKeyboardMarkup | InlineKeyboardMarkup | None:
    buttons = list(db_message.buttons.all())

    if not buttons:
        return None
    
    builder = InlineKeyboardBuilder()

    for button in db_message.buttons.all():
        builder.add(
            InlineKeyboardButton(
                text=button.text,
                url=button.url,
            )
        )
    return builder.as_markup()


async def send_message(
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
            msg = await message.answer_photo(
                photo=photo, caption=db_message.text, reply_markup=keyboard
            )
    else:
        msg = await message.answer(text=db_message.text, reply_markup=keyboard)

    return msg
