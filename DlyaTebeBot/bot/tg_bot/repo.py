from django.utils import timezone
from asgiref.sync import sync_to_async

from ..models import Message, TgUser, PromoCampaign


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
    def get_promocampaigns() -> list[PromoCampaign]:
        today = timezone.localdate()

        return list(
            PromoCampaign.objects.filter(
                start_date__lte=today, end_date__gte=today
            ).order_by("-start_date")
        )

    @staticmethod
    @sync_to_async
    def get_promo_by_pk(pk: int) -> PromoCampaign:
        return PromoCampaign.objects.get(pk=pk)

    @staticmethod
    @sync_to_async
    def get_user(telegram_id: int) -> TgUser | None:
        return TgUser.objects.filter(telegram_id=telegram_id).first()