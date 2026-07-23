from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware, Bot
from aiogram.types import Update, MessageReactionUpdated, InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger

from django.conf import settings

from .repo import TgUserRepo, TgMessageRepo


class UpdateLoggingMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable,
        event: Update,
        data: Dict[str, Any]
    ) -> Any:

        if event.message:
            await self._handle_new_message(event.message)

        if event.edited_message:
            await self._handle_edited_message(event.edited_message)

        if event.message_reaction:
            await self._handle_reaction(event.message_reaction)

        return await handler(event, data)

    async def _handle_new_message(self, message):

        if not message.from_user:
            return

        user = await TgUserRepo.get_user(
            telegram_id=message.from_user.id
        )

        # Пропускаємо повідомлення від бота
        if message.from_user.is_bot:
            return

        # Зберігаємо тільки реальні повідомлення від користувачів:
        # - Текстові повідомлення (не команди, не службові)
        # - Медіа файли (фото, відео, документи тощо)
        # Пропускаємо:
        # - Команди (/start, /help тощо)
        # - Службові повідомлення (контакти при реєстрації, кнопки меню)
        # - Повідомлення без тексту та медіа

        is_command = message.text and message.text.startswith('/')
        is_menu_button = message.text in ['main_menu', 'catalog', '♻️ Оновити меню']
        has_media = any([message.photo, message.video, message.document,
                        message.voice, message.audio, message.animation])
        has_real_text = message.text and not is_command and not is_menu_button

        # Пропускаємо службові повідомлення
        if not (has_real_text or has_media or message.caption):
            logger.debug(f"Skipping message - has_real_text={has_real_text}, has_media={has_media}, caption={bool(message.caption)}")
            return

        logger.info(f"Saving message from user {user.telegram_id if user else 'None'}")

        db_message = await TgMessageRepo.upsert_message(
            message_id=message.message_id,
            chat_id=message.chat.id,
            user=user,
            defaults={
                "chat_type": message.chat.type,
                "text": message.text,
                "caption": message.caption,
                "date": message.date,
                "raw_data": message.model_dump(),
            }
        )

        media_data = self._extract_media(message)

        if media_data:
            async with Bot(settings.BOT_TOKEN) as bot:

                enriched_media = []

                for media in media_data:
                    tg_file = await bot.get_file(media["file_id"])
                    file_path = tg_file.file_path
                    file_url = f"https://api.telegram.org/file/bot{settings.BOT_TOKEN}/{file_path}"

                    media["file_path"] = file_path
                    media["file_url"] = file_url

                    enriched_media.append(media)

            await TgMessageRepo.bulk_create_media(
                message_id=db_message.id,
                media_list=enriched_media
            )

        # Сповіщення адмінів про нове повідомлення
        logger.info(f"About to notify admins about message from user {user.telegram_id if user else 'None'}")
        await self._notify_admins_about_new_message(user, message)
        logger.info(f"Finished notifying admins")

    async def _handle_edited_message(self, message):

        await TgMessageRepo.mark_as_edited(
            message_id=message.message_id,
            chat_id=message.chat.id,
            text=message.text or message.caption,
            edit_date=message.edit_date
        )

    async def _handle_reaction(self, reaction: MessageReactionUpdated):

        if not reaction.user:
            return

        user = await TgUserRepo.get_user(
            telegram_id=reaction.user.id
        )

        message = await TgMessageRepo.get_message(
            message_id=reaction.message_id,
            chat_id=reaction.chat.id
        )

        if not message:
            return

        emojis = [
            r.emoji
            for r in reaction.new_reaction
            if hasattr(r, "emoji")
        ]

        await TgMessageRepo.replace_user_reactions(
            message_id=message.id,
            user=user,
            emojis=emojis
        )

    def _extract_media(self, message):

        media = []

        if message.photo:
            largest = message.photo[-1]
            media.append({
                "file_id": largest.file_id,
                "file_unique_id": largest.file_unique_id,
                "file_type": "photo",
                "file_size": largest.file_size,
            })

        if message.video:
            media.append({
                "file_id": message.video.file_id,
                "file_unique_id": message.video.file_unique_id,
                "file_type": "video",
                "file_name": message.video.file_name,
                "mime_type": message.video.mime_type,
                "file_size": message.video.file_size,
            })

        if message.document:
            media.append({
                "file_id": message.document.file_id,
                "file_unique_id": message.document.file_unique_id,
                "file_type": "document",
                "file_name": message.document.file_name,
                "mime_type": message.document.mime_type,
                "file_size": message.document.file_size,
            })

        if message.voice:
            media.append({
                "file_id": message.voice.file_id,
                "file_unique_id": message.voice.file_unique_id,
                "file_type": "voice",
                "file_size": message.voice.file_size,
            })

        if message.audio:
            media.append({
                "file_id": message.audio.file_id,
                "file_unique_id": message.audio.file_unique_id,
                "file_type": "audio",
                "file_name": message.audio.file_name,
                "mime_type": message.audio.mime_type,
                "file_size": message.audio.file_size,
            })

        if message.sticker:
            media.append({
                "file_id": message.sticker.file_id,
                "file_unique_id": message.sticker.file_unique_id,
                "file_type": "sticker",
            })

        if message.animation:
            media.append({
                "file_id": message.animation.file_id,
                "file_unique_id": message.animation.file_unique_id,
                "file_type": "animation",
                "file_name": message.animation.file_name,
                "mime_type": message.animation.mime_type,
                "file_size": message.animation.file_size,
            })

        return media

    async def _notify_admins_about_new_message(self, user, message):
        """Сповіщає всіх адмінів про нове повідомлення від користувача"""

        if not user:
            logger.warning("No user, skipping notification")
            return

        # Отримуємо всіх адмінів
        admin_users = await TgUserRepo.get_admin_users()

        logger.info(f"Found {len(admin_users)} admin users")

        if not admin_users:
            logger.warning("No admin users found")
            return

        # Формуємо текст сповіщення
        user_name = user.first_name or user.username or f"ID: {user.telegram_id}"
        message_preview = ""

        if message.text:
            message_preview = message.text[:100] + ("..." if len(message.text) > 100 else "")
        elif message.caption:
            message_preview = message.caption[:100] + ("..." if len(message.caption) > 100 else "")
        elif message.photo:
            message_preview = "📷 Фото"
        elif message.video:
            message_preview = "🎥 Відео"
        elif message.document:
            message_preview = "📎 Документ"
        elif message.voice:
            message_preview = "🎤 Голосове повідомлення"
        elif message.audio:
            message_preview = "🎵 Аудіо"

        notification_text = (
            f"💬 <b>Нове повідомлення від користувача</b>\n\n"
            f"👤 <b>Від:</b> {user_name}\n"
            f"📱 <b>Telegram ID:</b> <code>{user.telegram_id}</code>\n"
            f"📝 <b>Повідомлення:</b> {message_preview}"
        )

        # Створюємо кнопку з посиланням на чат
        admin_chat_url = f"{settings.ADMIN_URL}/bot/tguser/chat/{user.id}/"
        logger.info(f"Admin chat URL: {admin_chat_url}")

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💬 Відкрити чат", url=admin_chat_url)]
        ])

        # Відправляємо сповіщення всім адмінам
        async with Bot(settings.BOT_TOKEN) as bot:
            for admin in admin_users:
                try:
                    logger.info(f"Sending notification to admin {admin.telegram_id}")
                    await bot.send_message(
                        chat_id=admin.telegram_id,
                        text=notification_text,
                        parse_mode="HTML",
                        reply_markup=keyboard
                    )
                    logger.info(f"Successfully sent to admin {admin.telegram_id}")
                except Exception as e:
                    # Логуємо помилку, але не зупиняємо обробку повідомлення
                    logger.error(f"Failed to send to admin {admin.telegram_id}: {e}")
                    pass