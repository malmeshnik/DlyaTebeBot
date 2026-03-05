import hmac
import time
import hashlib
from init_data_py import InitData

from django.conf import settings


def check_telegram_auth(init_data: str, bot_token: str):
    try:
        init_data_obj = InitData.parse(init_data)

        if init_data_obj.validate(bot_token):
            return init_data_obj.to_dict()

        return None

    except Exception as e:
        print("Telegram auth error:", e)
        return None

def check_viber_auth(viber_id, ts, hash_value):

    if not viber_id or not ts or not hash_value:
        return None

    data = f"{viber_id}:{ts}"

    expected_hash = hmac.new(
        settings.VIBER_BOT_TOKEN.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_hash, hash_value):
        return None

    if time.time() - int(ts) > 300:
        return None

    return {
        "viber_id": viber_id
    }