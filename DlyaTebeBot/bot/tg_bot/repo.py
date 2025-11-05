from asgiref.sync import sync_to_async

from ..models import Message, TgUser

class MessageRepo:
    @staticmethod
    @sync_to_async
    def get_message_by_name(name: str) -> Message | None:
        try:
            return Message.objects.get(name=name)
        except Message.DoesNotExist:
            return None
        
class TgUserRepo:
    @staticmethod
    @sync_to_async
    def get_or_create_user(telegram_id: int, **kwargs) -> tuple[TgUser, bool]:
        user, created = TgUser.objects.get_or_create(
            telegram_id=telegram_id,
            defaults=kwargs
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