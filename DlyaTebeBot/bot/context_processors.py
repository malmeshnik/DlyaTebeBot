from django.db.models import Count, Q
from bot.models import TgUser
from viber_bot.models import ViberUser


def unread_messages(request):
    """Додає кількість непрочитаних повідомлень до контексту"""

    # Підраховуємо непрочитані Telegram повідомлення
    tg_unread = TgUser.objects.aggregate(
        total=Count('messages', filter=Q(messages__is_read=False, messages__is_bot=False))
    )['total'] or 0

    # Підраховуємо непрочитані Viber повідомлення
    viber_unread = ViberUser.objects.aggregate(
        total=Count('messages', filter=Q(messages__is_read=False, messages__is_bot=False))
    )['total'] or 0

    return {
        'tg_unread_count': tg_unread,
        'viber_unread_count': viber_unread,
    }
