from .models import ViberUser


class ViberUserRepo:
    @staticmethod
    def update_or_create(user_id, **data):
        return ViberUser.objects.update_or_create(viber_id=user_id, defaults=data)

    @staticmethod
    def get_phone(user_id):
        user = ViberUser.objects.get(viber_id=user_id)

        return user.phone_number
