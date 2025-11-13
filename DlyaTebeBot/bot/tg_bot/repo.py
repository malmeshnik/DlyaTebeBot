from django.utils import timezone
from asgiref.sync import sync_to_async

from ..models import Message, TgUser, PromoCampaign


class MessageRepo:
    """A repository for accessing `Message` models."""

    @staticmethod
    @sync_to_async
    def get_message_by_name(name: str) -> Message | None:
        """Retrieves a message from the database by its name.

        Args:
            name: The name of the message to retrieve.

        Returns:
            The `Message` object if found, otherwise `None`.
        """
        try:
            return Message.objects.get(name=name)
        except Message.DoesNotExist:
            return None


class TgUserRepo:
    """A repository for accessing `TgUser` models."""

    @staticmethod
    @sync_to_async
    def get_or_create_user(telegram_id: int, **kwargs) -> tuple[TgUser, bool]:
        """Retrieves or creates a user in the database.

        Args:
            telegram_id: The user's Telegram ID.
            **kwargs: Additional fields for creating the user.

        Returns:
            A tuple containing the `TgUser` object and a boolean indicating whether the user was created.
        """
        user, created = TgUser.objects.get_or_create(
            telegram_id=telegram_id, defaults=kwargs
        )

        return user, created

    @staticmethod
    @sync_to_async
    def get_user_phone(telegram_id: int) -> str | None:
        """Retrieves a user's phone number from the database.

        Args:
            telegram_id: The user's Telegram ID.

        Returns:
            The user's phone number if found, otherwise `None`.
        """
        try:
            user = TgUser.objects.get(telegram_id=telegram_id)
            return user.phone_number
        except TgUser.DoesNotExist:
            return None

    @staticmethod
    @sync_to_async
    def save_main_message(user_id: int, message_id: int) -> None:
        """Saves the main message ID for a user.

        Args:
            user_id: The user's Telegram ID.
            message_id: The ID of the main message.
        """
        TgUser.objects.filter(telegram_id=user_id).update(main_message_id=message_id)

    @staticmethod
    @sync_to_async
    def get_main_message_id(user_id: int) -> int:
        """Retrieves the main message ID for a user.

        Args:
            user_id: The user's Telegram ID.

        Returns:
            The ID of the main message.
        """
        user = TgUser.objects.get(telegram_id=user_id)

        return user.main_message_id

    @staticmethod
    @sync_to_async
    def get_promocampaigns() -> list[PromoCampaign]:
        """Retrieves a list of active promo campaigns.

        Returns:
            A list of `PromoCampaign` objects.
        """
        today = timezone.localdate()

        return list(
            PromoCampaign.objects.filter(
                start_date__lte=today, end_date__gte=today
            ).order_by("-start_date")
        )

    @staticmethod
    @sync_to_async
    def get_promo_by_pk(pk: int) -> PromoCampaign:
        """Retrieve a promo campaign by its primary key.

        Args:
            pk: The primary key of the promo campaign.

        Returns:
            The `PromoCampaign` object.
        """
        return PromoCampaign.objects.get(pk=pk)

    @staticmethod
    @sync_to_async
    def get_user(telegram_id: int) -> TgUser | None:
        """Retrieves a user from the database by their Telegram ID.

        Args:
            telegram_id: The user's Telegram ID.

        Returns:
            The `TgUser` object if found, otherwise `None`.
        """
        return TgUser.objects.filter(telegram_id=telegram_id).first()