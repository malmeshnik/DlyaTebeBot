import json
from io import BytesIO

import qrcode
from aiogram.types import BufferedInputFile


def generate_qr_code(phone: str) -> BufferedInputFile:
    """Generates a QR code containing the user's phone number.

    Args:
        phone: The user's phone number.

    Returns:
        A `BufferedInputFile` object representing the QR code image.
    """
    data = {"phone": phone}
    data_text = json.dumps(data, ensure_ascii=False)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=8,
        border=2,
    )

    qr.add_data(data_text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buf = BytesIO()
    img.save(buf, format="PNG")
    photo = BufferedInputFile(buf.getvalue(), filename="bonus_qr.png")

    return photo
