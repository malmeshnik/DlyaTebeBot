from typing import Optional, List
from dataclasses import dataclass

from .constants import SOCIAL_MEDIA_URLS
from .utils import generate_login_token
from .repo import ViberUserRepo

@dataclass
class Button:
    text: str = ""
    action: str = None
    action_type: str = None
    action_body: str = None
    columns: int = 6
    rows: int = 1
    bg_color: str = "#FFFFFF"
    text_color: str = "#FFFFFF"
    silent: bool = True
    text_bg_gradient_color: Optional[str] = None

    border_width: int = None
    border_color: str = None
    corner_radius: int = None

    text_size: str = "medium"
    text_h_align: str = "middle"
    text_v_align: str = "middle"

    image: str = None

    def to_dict(self) -> dict:
        data = {
            "Columns": self.columns,
            "Rows": self.rows,
            "Text": self.text,
            "BgColor": self.bg_color,
            "TextColor": self.text_color,
            "Silent": self.silent,
            "ActionType": self.action_type,
            "TextSize": self.text_size,
            "TextHAlign": self.text_h_align,
            "TextVAlign": self.text_v_align,
            "Image": self.image,
        }

        if self.action_body:
            data["ActionBody"] = self.action_body

        elif self.action_type == "share-phone":
            data["ActionBody"] = " "
        else:
            data["ActionBody"] = self.action

        if self.text_bg_gradient_color:
            data["TextBgGradientColor"] = self.text_bg_gradient_color

        data["Frame"] = {
            "BorderWidth": self.border_width,
            "BorderColor": self.border_color,
            "CornerRadius": self.corner_radius,
        }

        return data


class Keyboard:
    def __init__(self, default_height: bool = False):
        self.buttons: List[List[Button]] = []  # список рядків кнопок
        self.default_height = default_height

    def add(self, *buttons: Button):
        """Додає кнопки в новий рядок"""
        self.buttons.append(list(buttons))
        return self

    def row(self, *buttons: Button):
        """Синонім до add"""
        return self.add(*buttons)

    def adjust(self, columns: int = 6, rows: int = 1, resize: bool = True):
        """Підлаштувати клавіатуру під екран (DefaultHeight)"""
        self.default_height = resize
        return self.resize_buttons(columns, rows)

    def resize_buttons(self, columns: int = 6, rows: int = 2):
        """Задає розмір усім кнопкам"""
        for row in self.buttons:
            for btn in row:
                btn.columns = columns
                btn.rows = rows
        return self

    def to_dict(self) -> dict:
        kb_buttons = []
        for row in self.buttons:
            for btn in row:
                kb_buttons.append(btn.to_dict())
        return {
            "Type": "keyboard",
            "DefaultHeight": self.default_height,
            "BgColor": "#FFFFFF",
            "Buttons": kb_buttons,
        }

def create_menu_button(text: str, action_body: str) -> Button:
    return Button(
        text=f"<b>{text}</b>",
        action_type="reply",
        action_body=action_body,
        text_size="large",
    )

def main_menu(user_id):
    miniapp_token = ViberUserRepo.get_miniapp_token(user_id)
    kb = Keyboard()
    kb.add(
        create_menu_button("💳 Моя бонусна карта", "my_bonus_card"),
        create_menu_button("🎁 Акції", "promo"),
        create_menu_button("🛍️ Мої покупки", "my_purchaces"),
    ).row(
        Button(
            text="<b>📦 Каталог</b>",
            action_type="open-url",
            action_body=f"https://dlyatebebot.com/miniapp/?token={miniapp_token}",
            text_size="large",
            silent=True
        ),
        create_menu_button("☎️ Зв'язатися з нами", "contact_us"),
        create_menu_button("📱 Instagram, TikTok", "social_media"),
    )

    kb.adjust(columns=3, rows=1, resize=False)
    return kb.to_dict()


def contact():
    kb = Keyboard()
    kb.add(
        Button(
            text="📞 Відправити мій номер телефону",
            action=" ",
            action_type="share-phone",
        )
    )
    kb.resize_buttons(columns=6, rows=1)
    return kb.to_dict()
