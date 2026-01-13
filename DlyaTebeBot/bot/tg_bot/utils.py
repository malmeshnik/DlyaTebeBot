import mimetypes
import asyncio
import json
from io import BytesIO
from loguru import logger
from datetime import timedelta
from asgiref.sync import sync_to_async

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
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.conf import settings
from django.utils import timezone

from bots_settings.models import Message as DbMessage
from bots_settings.repo import MessageRepo, BroadCastMessageRepo, PromoCampaignRepo
from .repo import TgUserRepo


async def get_keyboard_for_message(
    db_message: DbMessage, broadcast: bool = False
) -> ReplyKeyboardMarkup | InlineKeyboardMarkup | None:
    buttons = await sync_to_async(list)(db_message.buttons.all())
    builder = InlineKeyboardBuilder()

    if buttons:

        for button in buttons:
            builder.add(
                InlineKeyboardButton(
                    text=button.text,
                    url=button.url,
                )
            )
    if not broadcast:
        builder.row(
            InlineKeyboardButton(text="⬅️ Повернутися в меню", callback_data="main_menu")
        )

    return builder.as_markup()


async def send_message_safe(
    bot: Bot,
    user,
    msg_text,
    keyboard=None,
    media_file=None,
    mime=None,
    send_button=True,
):
    """
    Очікує aiogram.Bot екземпляр в `bot`.
    Повертає aiogram Message при успіху або False при помилці.
    """
    logger.info(f"📤 Початок відправки повідомлення користувачу {user.telegram_id}")

    try:
        if media_file:
            logger.debug(f"📎 Відправка медіа типу {mime} для {user.telegram_id}")
            if mime and "image" in mime:
                sent = await bot.send_photo(
                    int(user.telegram_id),
                    media_file,
                    caption=msg_text,
                    reply_markup=keyboard,
                    parse_mode="HTML",
                )
            elif mime and "video" in mime:
                sent = await bot.send_video(
                    int(user.telegram_id),
                    media_file,
                    caption=msg_text,
                    reply_markup=keyboard,
                    parse_mode="HTML",
                )
            else:
                sent = await bot.send_document(
                    int(user.telegram_id),
                    media_file,
                    caption=msg_text,
                    reply_markup=keyboard,
                    parse_mode="HTML",
                )
        else:
            logger.debug("💬 Відправка текстового повідомлення")
            sent = await bot.send_message(
                int(user.telegram_id),
                msg_text,
                reply_markup=keyboard,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )

        logger.info(f"✅ Повідомлення успішно надіслано користувачу {user.telegram_id}")

    except TelegramForbiddenError as e:
        txt = str(e).lower()
        if "blocked" in txt:
            logger.warning(f"🚫 Користувач {user.telegram_id} заблокував бота")
        else:
            logger.warning(
                f"⛔ Доступ заборонено для користувача {user.telegram_id}: {e}"
            )
        return False

    except TelegramBadRequest as e:
        txt = str(e).lower()
        if "deactivated" in txt or "chat not found" in txt:
            logger.warning(f"❌ Аккаунт/чат {user.telegram_id} недоступний: {e}")
        else:
            logger.warning(f"🚫 Помилка запиту для {user.telegram_id}: {e}")
        return False

    except TelegramRetryAfter as e:
        wait = e.retry_after
        logger.warning(
            f"⏳ Flood control для {user.telegram_id}, очікування {wait} сек"
        )
        await asyncio.sleep(wait)
        logger.info(f"🔄 Повторна спроба надсилання для {user.telegram_id}")
        return await send_message_safe(
            bot, user, msg_text, keyboard, media_file, mime, send_button
        )

    except Exception as e:
        logger.error(
            f"❌ Невідома помилка при відправці {user.telegram_id}: {e}", exc_info=True
        )
        return False


async def send_message(
    message: Message,
    message_name: str,
    user_repo: TgUserRepo = None,
    photo: BufferedInputFile = None,
    keyboard: ReplyKeyboardMarkup | InlineKeyboardMarkup = None,
    bonus: int = None,
) -> Message:
    db_message = await DbMessage.objects.prefetch_related("buttons").aget(
        name=message_name
    )
    message_text = db_message.text.format(
        bonus=bonus, name=message.from_user.first_name
    )

    if not keyboard:
        keyboard = await get_keyboard_for_message(db_message)

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

    if message_name == "contact_received":
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
    logger.info(f"Editing message with name: {message_name}")
    db_message = await DbMessage.objects.prefetch_related("buttons").aget(
        name=message_name
    )
    message_text = db_message.text.format(bonus=bonus, name=message.chat.first_name)

    if not keyboard:
        keyboard = await get_keyboard_for_message(db_message)

    if db_message.image:
        mime_type, _ = mimetypes.guess_type(db_message.image.path)
        if mime_type and mime_type.startswith("image/"):
            photo = FSInputFile(db_message.image.path)
            media = InputMediaPhoto(media=photo, caption=message_text)
            try:
                msg = await message.edit_media(media=media, reply_markup=keyboard)
                msg = await message.edit_text(text=message_text, reply_markup=keyboard)
            except:
                await message.delete()
                msg = await message.answer_photo(photo=photo, caption=message_text, reply_markup=keyboard)
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
    db_message = await DbMessage.objects.prefetch_related("buttons").aget(
        name=db_message_name
    )

    if keyboard is None:
        keyboard = await get_keyboard_for_message(db_message)

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
    except TelegramBadRequest as e:
        logger.error(f"Error procesing edit message by id {e}")
        return None


def generate_qr_code(phone: str) -> BufferedInputFile:
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


async def check_and_send_promo():
    today = timezone.localdate()
    logger.info(f"Date now: {today}")
    tg_user_repo = TgUserRepo()
    promo_repo = PromoCampaignRepo()
    msg_repo = MessageRepo()

    promocampaigns = await promo_repo.aget_active_campaigns()
    logger.info(f"Find {len(promocampaigns)} active promo")

    for promo in promocampaigns:
        start = promo.start_date
        end = promo.end_date

        logger.info(
            f"[PromoCheck] {promo.name}: start={start}, end={end}, today={today}"
        )

        if promo.start_date == today:
            msg = await msg_repo.get_message_by_name("start_promo")
        elif promo.end_date == today:
            msg = await msg_repo.get_message_by_name("end_promo")
        elif promo.end_date - timedelta(days=3) == today:
            msg = await msg_repo.get_message_by_name("before_end_promo")
        else:
            continue

        logger.info(f"Sending message for promo: {promo.name}")
        users = await tg_user_repo.get_all_users()
        msg_text = msg.text.format(name_promo=promo.name, name="")
        async with Bot(settings.BOT_TOKEN) as bot:
            for user in users:
                await send_message_safe(bot=bot, user=user, msg_text=msg_text)


async def scheduler_messages():
    repo = BroadCastMessageRepo()
    tg_user_repo = TgUserRepo()
    ready_messages = await repo.aget_ready_messages()
    users = await tg_user_repo.get_all_users()

    async with Bot(token=settings.BOT_TOKEN) as bot:
        for message in ready_messages:
            message.send = True
            await sync_to_async(message.save)()

            media_file = FSInputFile(message.image.path) if message.image else None
            mime, _ = (
                mimetypes.guess_type(message.image.path)
                if message.image
                else (None, None)
            )

            for user in users:
                await send_message_safe(
                    bot=bot,
                    user=user,
                    msg_text=message.text,
                    keyboard=await get_keyboard_for_message(message, True),
                    media_file=media_file,
                    mime=mime,
                )
