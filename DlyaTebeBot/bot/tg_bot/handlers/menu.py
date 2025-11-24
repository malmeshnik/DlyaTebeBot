from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, FSInputFile, Message
from django.conf import settings

from bot.services.crm.client import CRMClient
from bot.tg_bot.keyboards.user import main_menu_keyboard, promo as promo_kb
from bot.tg_bot.repo import TgUserRepo
from bot.services.qr_service import generate_qr_code
from bot.tg_bot.utils import (
    edit_message,
    edit_message_by_id,
    send_message,
)

router = Router()
tg_user_repo = TgUserRepo()
crm_client = CRMClient(settings.PHONE_CRM_AUTH, settings.PASSWORD_CRM)


@router.callback_query(F.data == "main_menu")
async def main_menu_message(query: CallbackQuery) -> None:
    """Displays the main menu."""
    try:
        await edit_message(
            message=query.message,
            message_name="contact_received",
            user_repo=tg_user_repo,
            keyboard=main_menu_keyboard(),
        )
    except TelegramBadRequest:
        await query.message.delete()
        await send_message(
            message=query.message,
            message_name="contact_received",
            user_repo=tg_user_repo,
            keyboard=main_menu_keyboard(),
        )


@router.message(F.text == "main_menu")
async def main_menu(message: Message, bot: Bot) -> None:
    """Displays the main menu."""
    await message.delete()

    await edit_message_by_id(
        bot=bot,
        chat_id=message.chat.id,
        message_id=message.message_id,
        db_message_name="start",
        keyboard=main_menu_keyboard(),
    )


@router.callback_query(F.data == "mu_bonus_card")
async def bonus_card_message(query: CallbackQuery) -> None:
    """Displays the user's bonus card."""
    await query.answer()

    phone = await tg_user_repo.get_user_phone(telegram_id=query.from_user.id)
    consumer = crm_client.get_consumer_info(phone)
    photo = generate_qr_code(phone)

    await query.message.delete()
    await send_message(
        message=query.message,
        message_name="bonus_card",
        user_repo=tg_user_repo,
        photo=photo,
        bonus=consumer.bonus,
    )


@router.callback_query(F.data == "catalog")
async def catalog(query: CallbackQuery) -> None:
    """Displays the catalog."""
    await edit_message(
        message=query.message, message_name="catalog", user_repo=tg_user_repo
    )


@router.callback_query(F.data == "contact_us")
async def contact_request_message(query: CallbackQuery) -> None:
    """Displays the contact request message."""
    await edit_message(
        message=query.message,
        message_name="contact_request",
        user_repo=tg_user_repo,
    )


@router.callback_query(F.data == "social_media")
async def social_media_message(query: CallbackQuery) -> None:
    """Displays the social media links."""
    await edit_message(
        message=query.message, message_name="social_media", user_repo=tg_user_repo
    )


@router.message(F.text.startswith("promo:"))
async def view_promo(message: Message, bot: Bot) -> None:
    """Displays a specific promotion."""
    await message.delete()
    try:
        user_id = message.chat.id
        main_message_id = await tg_user_repo.get_main_message_id(user_id)
        await bot.delete_message(user_id, main_message_id)
    except:
        pass

    keyboard = promo_kb()
    pk = message.text.split(":")[1]
    promocampaign = await tg_user_repo.get_promo_by_pk(pk)
    message_text = f"<b>{promocampaign.name}</b>\n\n{promocampaign.description}"

    if promocampaign.image:
        photo = FSInputFile(promocampaign.image.path)
        await message.answer_photo(
            photo=photo, caption=message_text, reply_markup=keyboard
        )
        return

    await message.answer(message_text, reply_markup=keyboard)
