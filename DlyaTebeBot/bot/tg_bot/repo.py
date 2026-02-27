from typing import Optional, Iterable
from asgiref.sync import sync_to_async
from django.db import transaction

from ..models import TgUser, TgMessage, TgMessageMedia, TgMessageReaction


class TgUserRepo:
    @staticmethod
    @sync_to_async
    def get_or_create_user(telegram_id: int, **kwargs) -> tuple[TgUser, bool]:
        user, created = TgUser.objects.get_or_create(
            telegram_id=telegram_id, defaults=kwargs
        )

        return user, created
    
    @staticmethod
    def get_or_create(telegram_id: int, **kwargs) -> tuple[TgUser, bool]:
        user, created = TgUser.objects.get_or_create(
            telegram_id=telegram_id, defaults=kwargs
        )

        return user, created

    @staticmethod
    @sync_to_async
    def get_user_phone(telegram_id: int) -> str | None:
        try:
            user = TgUser.objects.get(telegram_id=telegram_id)
            return user.phone_number
        except TgUser.DoesNotExist:
            return None

    @staticmethod
    @sync_to_async
    def save_main_message(user_id: int, message_id: int) -> None:
        TgUser.objects.filter(telegram_id=user_id).update(main_message_id=message_id)

    @staticmethod
    @sync_to_async
    def get_main_message_id(user_id: int) -> int:
        user = TgUser.objects.get(telegram_id=user_id)

        return user.main_message_id
    
    @staticmethod
    @sync_to_async
    def get_user(telegram_id: int) -> TgUser | None:
        users = TgUser.objects.filter(telegram_id=telegram_id)
        
        return users.first() if users else None

    @staticmethod
    @sync_to_async
    def get_all_users() -> list[TgUser]:
        return list(TgUser.objects.all())

    @staticmethod
    @sync_to_async
    def get_admins() -> list[TgUser]:
        return list(TgUser.objects.filter(is_admin=True))
    
class TgMessageRepo:

    @staticmethod
    @sync_to_async
    def upsert_message(
        message_id: int,
        chat_id: int,
        defaults: dict,
        user: Optional[TgUser] = None,
    ) -> TgMessage:

        defaults["user"] = user

        obj, _ = TgMessage.objects.update_or_create(
            message_id=message_id,
            chat_id=chat_id,
            defaults=defaults
        )

        return obj
    
    @staticmethod
    @sync_to_async
    def mark_as_edited(
        message_id: int,
        chat_id: int,
        text: Optional[str],
        edit_date
    ) -> None:

        TgMessage.objects.filter(
            message_id=message_id,
            chat_id=chat_id
        ).update(
            text=text,
            is_edited=True,
            edit_date=edit_date
        )

    @staticmethod
    @sync_to_async
    def bulk_create_media(
        message_id: int,
        media_list: Iterable[dict]
    ) -> None:

        objects = [
            TgMessageMedia(
                message_id=message_id,
                **media_data
            )
            for media_data in media_list
        ]

        TgMessageMedia.objects.bulk_create(
            objects,
            ignore_conflicts=True
        )

    @staticmethod
    @sync_to_async
    @transaction.atomic
    def replace_user_reactions(
        message_id: int,
        user: TgUser,
        emojis: list[str]
    ) -> None:

        TgMessageReaction.objects.filter(
            message_id=message_id,
            user=user
        ).delete()

        if not emojis:
            return

        TgMessageReaction.objects.bulk_create(
            [
                TgMessageReaction(
                    message_id=message_id,
                    user=user,
                    emoji=emoji
                )
                for emoji in emojis
            ]
        )

    @staticmethod
    @sync_to_async
    def get_message(
        message_id: int,
        chat_id: int
    ) -> Optional[TgMessage]:

        return (
            TgMessage.objects
            .select_related("user")
            .only("id", "message_id", "chat_id", "user")
            .filter(
                message_id=message_id,
                chat_id=chat_id
            )
            .first()
        )