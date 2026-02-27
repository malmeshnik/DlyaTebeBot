import hmac
import hashlib
import time
from typing import Optional, Dict
from urllib.parse import parse_qsl


def _parse_init_data(init_data: str) -> Dict[str, str]:
    return dict(parse_qsl(init_data, keep_blank_values=True))


def check_telegram_auth(init_data: str, bot_token: str, max_age_seconds: int = 86400) -> Optional[Dict[str, str]]:
    if not init_data or not bot_token:
        return None

    if isinstance(init_data, dict):
        data = init_data
    else:
        try:
            data = _parse_init_data(init_data)
        except Exception:
            return None

    received_hash = data.pop("hash", None)
    if not received_hash:
        return None

    items = sorted((k, v) for k, v in data.items())
    data_check_string = "\n".join(f"{k}={v}" for k, v in items)

    secret_key = hashlib.sha256(bot_token.encode()).digest()
    calc_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calc_hash, received_hash):
        return None

    auth_date = data.get("auth_date")
    if auth_date:
        try:
            auth_ts = int(auth_date)
            if time.time() - auth_ts > max_age_seconds:
                return None
        except Exception:
            return None

    return data