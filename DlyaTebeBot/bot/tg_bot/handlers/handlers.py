from loguru import logger
from random import randint

from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery,
    Message,
    ReplyKeyboardRemove,
    InlineQuery,
    InputTextMessageContent,
    InlineQueryResultArticle,
    FSInputFile,
)
from aiogram.filters.command import CommandStart
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from django.conf import settings

from ..repo import MessageRepo, TgUserRepo
from ..keyboards.user import get_contact_keyboard, main_menu_keyboard, promo as promo_kb
from ..states import UserStates
from ..utils import send_message, edit_message, edit_message_by_id, generate_qr_code
from ...api import ApiCRM


router = Router()
msg_repo = MessageRepo()
tg_user_repo = TgUserRepo()
crm_client = ApiCRM(settings.PHONE_CRM_AUTH, settings.PASSWORD_CRM)


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


@router.message(UserStates.contact)
async def handle_contact(message: Message, state: FSMContext) -> None:
    """Handles the user's contact information.

    It extracts the phone number from the message, creates a new user in the database,
    and displays the main menu.

    Args:
        message: The incoming message object.
        state: The FSM context for managing user states.
    """
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


@router.callback_query(F.data == "main_menu")
async def main_menu_message(query: CallbackQuery) -> None:
    """Displays the main menu.

    It edits the current message to show the main menu.

    Args:
        query: The incoming callback query.
    """
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
    """Displays the main menu.

    It deletes the incoming message and edits the previous one to show the main menu.

    Args:
        message: The incoming message object.
        bot: The bot instance.
    """
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
    """Displays the user's bonus card.

    It retrieves the user's phone number, fetches their bonus card information from the CRM,
    generates a QR code, and sends it to the user.

    Args:
        query: The incoming callback query.
    """
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
    """Displays the catalog.

    It edits the current message to show the catalog.

    Args:
        query: The incoming callback query.
    """
    await edit_message(
        message=query.message, message_name="catalog", user_repo=tg_user_repo
    )


@router.callback_query(F.data == "contact_us")
async def contact_request_message(query: CallbackQuery) -> None:
    """Displays the contact request message.

    It edits the current message to show the contact request.

    Args:
        query: The incoming callback query.
    """
    await edit_message(
        message=query.message,
        message_name="contact_request",
        user_repo=tg_user_repo,
    )


@router.callback_query(F.data == "social_media")
async def social_media_message(query: CallbackQuery) -> None:
    """Displays the social media links.

    It edits the current message to show the social media links.

    Args:
        query: The incoming callback query.
    """
    await edit_message(
        message=query.message, message_name="social_media", user_repo=tg_user_repo
    )


@router.inline_query(F.query.startswith("promo"))
async def promo(query: InlineQuery):
    """Handles the inline query for promotions.

    It retrieves a list of active promotions and displays them as inline query results.

    Args:
        query: The incoming inline query.
    """
    results = [
        InlineQueryResultArticle(
            id="promo",
            title="🎁 АКЦІЇ",
            description="Для повного перегляду акції виберіть її",
            thumbnail_url="https://upload.wikimedia.org/wikipedia/commons/5/59/Empty.png",
            input_message_content=InputTextMessageContent(
                message_text="main_menu",
            ),
        ),
    ]
    promocampaigns = await tg_user_repo.get_promocampaigns()
    if not promocampaigns:
        results = [
            InlineQueryResultArticle(
                id="a1",
                title="🎁 АКЦІЇ",
                description="Поки що немає активних акцій, як тільки вони з'являться ми вас сповістимо",
                thumbnail_url="https://upload.wikimedia.org/wikipedia/commons/5/59/Empty.png",
                input_message_content=InputTextMessageContent(
                    message_text="main_menu",
                ),
            ),
        ]

    logger.info(f"Found {len(promocampaigns)} promo")

    for promo in promocampaigns:
        desc = (promo.description or "")[:512]

        results.append(
            InlineQueryResultArticle(
                id=f"promo-{promo.id}",
                thumbnail_url=promo.image_url,
                title=promo.name,
                description=desc,
                input_message_content=InputTextMessageContent(
                    message_text=f"promo:{promo.id}",
                ),
            )
        )

    await query.answer(results=results, cache_time=1, is_personal=True)


@router.message(F.text.startswith("promo:"))
async def view_promo(message: Message, bot: Bot) -> None:
    """Displays a specific promotion.

    It retrieves the promotion details from the database and sends them to the user.

    Args:
        message: The incoming message object.
        bot: The bot instance.
    """
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


@router.inline_query(F.query.startswith("my_purchaces"))
async def inline_my_purchaces(query: InlineQuery):
    """Handles the inline query for user purchases.

    It retrieves the user's purchase history from the CRM and displays it as inline query results.

    Args:
        query: The incoming inline query.
    """
    user_phone = await tg_user_repo.get_user_phone(query.from_user.id)
    cunsomer = crm_client.get_consumer_info(user_phone)

    results = [
        InlineQueryResultArticle(
            id="my_purchaces",
            title="Мої покупки",
            description="Тут відображаются останні 5 ваших покупок якщо вони існують",
            thumbnail_url="https://upload.wikimedia.org/wikipedia/commons/5/59/Empty.png",
            input_message_content=InputTextMessageContent(
                message_text="main_menu",
            ),
        )
    ]

    if not cunsomer.purchaces:
        results.append(
            InlineQueryResultArticle(
                id="None-purchase",
                title="Ви ще не зробили жодної покупки 😔",
                description="Натисніть на це меню щоб відкрити наш каталог 🤗",
                thumbnail_url="https://upload.wikimedia.org/wikipedia/commons/5/59/Empty.png",
                input_message_content=InputTextMessageContent(
                    message_text="catalog",
                ),
            )
        )

    for purchace in cunsomer.purchaces:
        for product in purchace.products:
            if not product.product.isdigit():
                results.append(
                    InlineQueryResultArticle(
                        id=f"purchace-{randint(1, 10000)}",
                        title=product.product,
                        description=f"Кількість: {product.quantity} Вартість: {product.price}",
                        thumbnail_url="https://upload.wikimedia.org/wikipedia/commons/5/59/Empty.png",
                        input_message_content=InputTextMessageContent(
                            message_text="main_menu",
                        ),
                    )
                )

    await query.answer(results=results, cache_time=1, is_personal=True)