from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken
from django.conf import settings
import jwt

from bot.tg_bot.repo import TgUserRepo

class TelegramJWTAuthentication(BaseAuthentication):

    def authenticate(self, request):

        header = request.headers.get("Authorization")

        if not header:
            return None

        token = header.split()[1]

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )
        except jwt.PyJWTError:
            raise InvalidToken()

        telegram_id = payload.get("telegram_id")

        if not telegram_id:
            return None

        user = TgUserRepo.get_by_telegram_id(telegram_id)

        return (user, None)