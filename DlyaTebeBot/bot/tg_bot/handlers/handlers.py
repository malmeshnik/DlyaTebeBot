from uuid import uuid4
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
from aiogram.filters.command import CommandStart, CommandObject
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from django.conf import settings
from django.utils import timezone

from bots_settings.repo import MessageRepo, PromoCampaignRepo
from ..repo import TgUserRepo
from ..keyboards.user import get_contact_keyboard, main_menu_keyboard, restart_menu_keyboard, promo_keybord, promo as promo_kb
from ..states import UserStates
from ..utils import send_message, edit_message, edit_message_by_id, generate_qr_code
from ...api import ApiCRM
from miniapp.models import WheelSpin


router = Router()
msg_repo = MessageRepo()
promo_repo = PromoCampaignRepo()
tg_user_repo = TgUserRepo()
crm_client = ApiCRM(settings.PHONE_CRM_AUTH, settings.PASSWORD_CRM)


@router.message(CommandStart())
async def start(message: Message, state: FSMContext, command: CommandObject) -> None:
    await message.delete()
    user = await tg_user_repo.get_user(message.from_user.id)

    # Перевірка чи це код виграшу з колеса фортуни
    if command.args and command.args.startswith('W'):
        code = command.args

        # Спочатку перевіряємо чи користувач зареєстрований
        if not user or not user.phone_number:
            await send_message(
                message=message,
                message_name="start",
                user_repo=tg_user_repo,
                keyboard=get_contact_keyboard(),
            )
            await state.set_state(UserStates.contact)
            # Зберігаємо код для використання після реєстрації
            await state.update_data(wheel_code=code)
            return

        # Обробка коду виграшу
        await handle_wheel_prize(message, user, code)
        return

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


async def handle_wheel_prize(message: Message, user, code: str):
    """Обробка коду виграшу з колеса фортуни"""
    try:
        spin = await WheelSpin.objects.select_related('prize').aget(code=code, is_claimed=False)

        # Прив'язуємо виграш до користувача
        spin.tg_user = user
        spin.is_claimed = True
        spin.claimed_at = timezone.now()
        prize = spin.prize
        await spin.asave()

        if prize.win_image:
            photo = FSInputFile(prize.win_image.path)
            await message.answer_photo(
                photo=photo,
                caption=prize.message_text.format(prize_name=prize.name),
                parse_mode="HTML",
                reply_markup=main_menu_keyboard()
            )
        else:
            await message.answer(
                prize.message_text.format(prize_name=prize.name),
                parse_mode="HTML",
                reply_markup=main_menu_keyboard()
            )


        logger.info(f"User {user.telegram_id} claimed prize {spin.prize.name} with code {code}")

    except WheelSpin.DoesNotExist:
        await message.answer(
            "❌ <b>Невірний або вже використаний код.</b>\n\n"
            "Можливо, ви вже активували цей приз раніше, або код введено невірно.",
            parse_mode="HTML",
            reply_markup=main_menu_keyboard()
        )
        logger.warning(f"User {user.telegram_id if user else 'unknown'} tried invalid code: {code}")
    except Exception as e:
        logger.error(f"Error handling wheel prize: {e}")
        await message.answer(
            "❌ <b>Виникла помилка при активації призу.</b>\n\n"
            "Будь ласка, спробуйте пізніше або зверніться до адміністратора.",
            parse_mode="HTML",
            reply_markup=main_menu_keyboard()
        )


@router.message(UserStates.contact)
async def handle_contact(message: Message, bot: Bot, state: FSMContext) -> None:
    await message.delete()
    try:
        await bot.delete_message(message.chat.id, message.message_id - 1)
    except TelegramBadRequest:
        pass

    msg = await msg_repo.aget_message_by_name("contact_received")

    try:
        phone_number = message.contact.phone_number
    except AttributeError:
        phone_number = message.text if message.text.startswith("380") else None
    except Exception as e:
        logger.error(f"Error retrieving contact: {e}")
        phone_number = None

    tg_user, created = await tg_user_repo.aupdate_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        phone_number=phone_number,
    )

    if created:
        logger.info(f"New user created: {tg_user.first_name}")

    # Перевірка чи є збережений код виграшу
    data = await state.get_data()
    wheel_code = data.get('wheel_code')

    if wheel_code:
        # Активуємо приз після реєстрації
        await handle_wheel_prize(message, tg_user, wheel_code)
        await state.update_data(wheel_code=None)
        return

    if phone_number:
        try:
            await send_message(
                    message=message,
                    message_name="hello",
                    user_repo=tg_user_repo,
                    keyboard=restart_menu_keyboard(),
                )
        except:
            pass

        await send_message(
            message=message,
            message_name="contact_received",
            user_repo=tg_user_repo,
            keyboard=main_menu_keyboard(),
        )
    await state.clear()


@router.callback_query(F.data == "main_menu")
async def main_menu_message(query: CallbackQuery) -> None:
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
    await message.delete()

    await edit_message_by_id(
        bot=bot,
        chat_id=message.chat.id,
        message_id=message.message_id,
        db_message_name="start",
        keyboard=main_menu_keyboard(),
    )

@router.message(F.text == 'catalog')
async def catalog(message: Message, bot: Bot) -> None:
    await message.delete()
    main_menu_id = await tg_user_repo.get_main_message_id(message.from_user.id)

    await edit_message_by_id(
        bot=bot,
        chat_id=message.chat.id,
        message_id=main_menu_id,
        db_message_name="catalog"
    )


@router.callback_query(F.data == "mu_bonus_card")
async def bonus_card_message(query: CallbackQuery) -> None:
    await query.answer()

    phone = await tg_user_repo.get_user_phone(telegram_id=query.from_user.id)
    consumer = crm_client.get_consumer_info(phone)
    bonus_value = consumer.bonus if consumer else 0
    photo = generate_qr_code(phone)

    try:
        await query.message.delete()
    except:
        pass
        
    await send_message(
        message=query.message,
        message_name="bonus_card",
        user_repo=tg_user_repo,
        photo=photo,
        bonus=bonus_value,
    )


@router.callback_query(F.data == "catalog")
async def catalog(query: CallbackQuery) -> None:
    await edit_message(
        message=query.message, message_name="catalog", user_repo=tg_user_repo
    )


@router.callback_query(F.data == "contact_us")
async def contact_request_message(query: CallbackQuery) -> None:
    await edit_message(
        message=query.message,
        message_name="contact_request",
        user_repo=tg_user_repo,
    )


@router.callback_query(F.data == "social_media")
async def social_media_message(query: CallbackQuery) -> None:
    await edit_message(
        message=query.message, message_name="social_media", user_repo=tg_user_repo
    )


@router.callback_query(F.data == "promo")
async def promo(query: CallbackQuery):
    await query.answer()
    promocampaigns = await promo_repo.aget_active_campaigns()
    if not promocampaigns:
        await edit_message(
            message=query.message, 
            message_name="no_promo", 
            user_repo=tg_user_repo, 
            keyboard=main_menu_keyboard()
        )
        return

    await edit_message(
        message=query.message,
        message_name="promo",
        user_repo=tg_user_repo,
        keyboard=promo_keybord(promocampaigns)
    )


@router.callback_query(F.data.startswith("promo:"))
async def view_promo(query: CallbackQuery) -> None:
    await query.answer()

    keyboard = promo_keybord([])
    pk = query.data.split(":")[1]
    promocampaign = await promo_repo.aget_promo(pk)
    message_text = f"<b>{promocampaign.name}</b>\n\n{promocampaign.description}"

    if promocampaign.image:
        await query.message.delete()
        photo = FSInputFile(promocampaign.image.path)
        await query.message.answer_photo(
            photo=photo, caption=message_text, reply_markup=keyboard
        )
        return

    await edit_message(
        message=query.message,
        message_text=message_text,
        user_repo=tg_user_repo,
        keyboard=keyboard
    )


@router.inline_query(F.query.startswith("my_purchaces"))
async def inline_my_purchaces(query: InlineQuery):
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

    for purchace in cunsomer.purchaces[:5]:
        for product in purchace.products:
            if product.product:
                product_name = product.product if not product.product.isdigit() else f"Парфюм {product.product}"

                results.append(
                    InlineQueryResultArticle(
                        id=str(uuid4()),
                        title=product.product,
                        description=f"Кількість: {product.quantity} Вартість: {product.price}",
                        thumbnail_url="https://upload.wikimedia.org/wikipedia/commons/5/59/Empty.png",
                        input_message_content=InputTextMessageContent(
                            message_text="main_menu",
                        ),
                    )
                )

    await query.answer(results=results[:20], cache_time=1, is_personal=True)

@router.message(F.text == "♻️ Оновити меню")
async def restart_menu(message: Message):
    keyboard = main_menu_keyboard()
    await message.answer("Меню оновлено!", reply_markup=keyboard)