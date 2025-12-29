from asgiref.sync import sync_to_async

from ..models import TgUser


class TgUserRepo:
    @staticmethod
    @sync_to_async
    def get_or_create_user(telegram_id: int, **kwargs) -> tuple[TgUser, bool]:
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
        return TgUser.objects.filter(telegram_id=telegram_id).first()

    @staticmethod
    @sync_to_async
    def get_all_users() -> list[TgUser]:
        return list(TgUser.objects.all())