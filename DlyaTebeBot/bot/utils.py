from django.db.models import Count, Q
from loguru import logger


def get_tg_unread_count(request=None):
    """Повертає кількість непрочитаних Telegram повідомлень"""
    from bot.models import TgUser
    count = TgUser.objects.aggregate(
        total=Count('messages', filter=Q(messages__is_read=False, messages__is_bot=False))
    )['total'] or 0
    logger.info(f"Telegram unread count: {count}")
    return count if count > 0 else 0


def get_viber_unread_count(request=None):
    """Повертає кількість непрочитаних Viber повідомлень"""
    from viber_bot.models import ViberUser
    count = ViberUser.objects.aggregate(
        total=Count('messages', filter=Q(messages__is_read=False, messages__is_bot=False))
    )['total'] or 0
    logger.info(f"Viber unread count: {count}")
    return count if count > 0 else 0
