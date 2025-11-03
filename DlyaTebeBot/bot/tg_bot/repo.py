from asgiref.sync import sync_to_async

from ..models import Message

class MessageRepo:
    @staticmethod
    @sync_to_async
    def get_message_by_name(name: str) -> Message | None:
        try:
            return Message.objects.get(name=name)
        except Message.DoesNotExist:
            return None