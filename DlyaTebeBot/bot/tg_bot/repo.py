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
    def get_or_create_user(telegram_id: int, **kwargs) -> TgUser:
        user, created = TgUser.objects.get_or_create(
            telegram_id=telegram_id,
            defaults=kwargs
        )

        return user, created