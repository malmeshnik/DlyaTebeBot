from django.utils import timezone

from .models import ViberUser, PromoCampaign


class ViberUserRepo:
    @staticmethod
    def update_or_create(user_id, **data):
        return ViberUser.objects.update_or_create(viber_id=user_id, defaults=data)

    @staticmethod
    def get_phone(user_id):
        user = ViberUser.objects.get(viber_id=user_id)

        return user.phone_number


class PromoCampaignRepo:
    @staticmethod
    def get_active_campaigns():
        today = timezone.now().date()
        return list(
            PromoCampaign.objects.filter(start_date__lte=today, end_date__gte=today)
        )
