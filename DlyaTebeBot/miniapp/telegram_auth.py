import hmac
import hashlib
import time
from typing import Optional, Dict
from urllib.parse import parse_qsl


def _parse_init_data(init_data: str) -> Dict[str, str]:
    return dict(parse_qsl(init_data, keep_blank_values=True))


def check_telegram_auth(init_data: str, bot_token: str) -> dict | None:
    data = dict(parse_qsl(init_data, keep_blank_values=True))

    received_hash = data.pop("hash", None)
    data.pop("signature", None)

    if not received_hash:
        return None

    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(data.items())
    )

    secret_key = hmac.new(
        key=b"WebAppData",
        msg=bot_token.encode(),
        digestmod=hashlib.sha256
    ).digest()

    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        return None

    auth_date = data.get("auth_date")
    if not auth_date:
        return None

    try:
        auth_timestamp = int(auth_date)
        current_timestamp = int(time.time())
        # Replay protection: check if auth_date is within the last 24 hours
        if abs(current_timestamp - auth_timestamp) > 86400:
            return None
    except (ValueError, TypeError):
        return None

    return data
