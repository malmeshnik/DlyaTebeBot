from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
)


def get_contact_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Відправити номер телефону", request_contact=True))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="💳 Моя бонусна карта", callback_data="mu_bonus_card")
    )
    builder.add(
        InlineKeyboardButton(text="🎁 Акції", switch_inline_query_current_chat="promo")
    )
    builder.add(
        InlineKeyboardButton(text="🛍️ Мої покупки", callback_data="my_purchases")
    )
    builder.add(InlineKeyboardButton(text="📦 Каталог", callback_data="catalog"))
    builder.add(
        InlineKeyboardButton(text="☎️ Зв'язатися з нами", callback_data="contact_us")
    )
    builder.add(
        InlineKeyboardButton(text="📱 Instagram, TikTok", callback_data="social_media")
    )

    builder.adjust(2, 2, 2)
    return builder.as_markup()


def promo() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="📦 Каталог", callback_data="catalog"))
    builder.add(
        InlineKeyboardButton(text="⬅️ Повернутися в меню", callback_data="main_menu")
    )

    builder.adjust(1)

    return builder.as_markup()
