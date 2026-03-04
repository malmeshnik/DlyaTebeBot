from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware, Bot
from aiogram.types import Update, MessageReactionUpdated

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

        if not media_data:
            return

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