try:
    from unfold.admin import UnfoldAdminSite
except ImportError:
    from unfold.sites import UnfoldAdminSite

from django.db.models import Count, Q


class CustomAdminSite(UnfoldAdminSite):
    def each_context(self, request):
        context = super().each_context(request)

        # Додаємо кількість непрочитаних повідомлень
        from bot.models import TgUser
        from viber_bot.models import ViberUser

        tg_unread = TgUser.objects.aggregate(
            total=Count('messages', filter=Q(messages__is_read=False, messages__is_bot=False))
        )['total'] or 0

        viber_unread = ViberUser.objects.aggregate(
            total=Count('messages', filter=Q(messages__is_read=False, messages__is_bot=False))
        )['total'] or 0

        context['tg_unread_count'] = tg_unread
        context['viber_unread_count'] = viber_unread

        return context
