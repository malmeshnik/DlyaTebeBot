from .models import ViberUser, ViberMessage


class ViberUserRepo:
    @staticmethod
    def update_or_create(user_id, **data):
        return ViberUser.objects.update_or_create(viber_id=user_id, defaults=data)

    @staticmethod
    def get_phone(user_id):
        user = ViberUser.objects.get(viber_id=user_id)

        return user.phone_number

    @staticmethod
    def get(user_id):
        user = ViberUser.objects.filter(viber_id=user_id).first()

        return user

    @staticmethod
    def get_miniapp_token(user_id):
        user = ViberUser.objects.filter(viber_id=user_id).first()

        return user.miniapp_token

    @staticmethod
    def get_by_miniapp_token(token):
        user = ViberUser.objects.filter(miniapp_token=token).first()

        return user


class ViberMessageRepo:
    @staticmethod
    def create(user, text, media_url=None, is_bot=False, timestamp=None):
        return ViberMessage.objects.create(
            user=user,
            text=text,
            media_url=media_url,
            is_bot=is_bot,
            timestamp=timestamp
        )
