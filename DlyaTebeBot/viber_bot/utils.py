import os
import qrcode
import hmac
import hashlib
import time

from django.conf import settings


def generate_qr_code(phone_number: str) -> str:
    """
    Генерує QR-код для номера телефону, зберігає у MEDIA і відправляє у Viber.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data({"phone": phone_number})
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    filename = f"qr_codes/{phone_number}.png"
    filepath = os.path.join(settings.MEDIA_ROOT, filename)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    img.save(filepath)

    qr_url = settings.MEDIA_URL + filename

    return qr_url

def generate_login_token(user_id):

    ts = int(time.time())

    data = f"{user_id}:{ts}"

    signature = hmac.new(
        settings.VIBER_BOT_TOKEN.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()

    return user_id, ts, signature