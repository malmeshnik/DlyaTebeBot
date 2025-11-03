from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_contact_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Відправити номер телефону", request_contact=True))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)