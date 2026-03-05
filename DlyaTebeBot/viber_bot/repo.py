from .models import ViberUser, ViberMessage


class ViberUserRepo:
    @staticmethod
    def update_or_create(user_id, **data):
        return ViberUser.objects.update_or_create(viber_id=user_id, defaults=data)

    @staticmethod
    def get_phone(user_id):
        user = ViberUser.objects.get(viber_id=user_id)

        return user.phone_number


class ViberMessageRepo:
    @staticmethod
    def create(user, text, media_url, is_bot=False, timestamp=None):
        return ViberMessage.objects.create(
            user=user,
            text=text,
            media_url=media_url,
            is_bot=is_bot,
            timestamp=timestamp
        )
