from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_contact_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Відправити номер телефону", request_contact=True))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Моя бонусна карта"))
    builder.add(KeyboardButton(text="Акції"))
    builder.add(KeyboardButton(text="Мої покупки"))
    builder.add(KeyboardButton(text="Каталог"))
    builder.add(KeyboardButton(text="Зв'язатися з нами"))
    builder.add(KeyboardButton(text="Instagram, TikTok"))

    builder.adjust(2, 2, 2)
    return builder.as_markup(resize_keyboard=True)