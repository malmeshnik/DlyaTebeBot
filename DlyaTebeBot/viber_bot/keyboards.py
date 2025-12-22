from typing import Optional, List
from dataclasses import dataclass


@dataclass
class Button:
    text: str
    action: str
    columns: int = 6
    rows: int = 2
    bg_color: str = '#0A5ED7'
    text_color: str = '#FFFFFF'
    silent: bool = True
    text_bg_gradient_color: Optional[str] = None
    action_type: str = "reply"

    def to_dict(self) -> dict:
        data = {
            "Columns": self.columns,
            "Rows": self.rows,
            "Text": self.text,
            "BgColor": self.bg_color,
            "TextColor": self.text_color,
            "Silent": self.silent,
            "ActionType": self.action_type,
        }
        if self.action_type == "share-phone":
            data["ActionBody"] = " "
        else:
            data["ActionBody"] = self.action
        if self.text_bg_gradient_color:
            data["TextBgGradientColor"] = self.text_bg_gradient_color
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
            "Buttons": kb_buttons,
        }



def main_menu():
    kb = Keyboard()
    kb.add(
        Button(text="💳 Моя бонусна карта", action="my_bonus_card"),
        Button(text="🎁 Акції", action="promo"),
        Button(text="🛍️ Мої покупки", action="my_purchaces"),
    ).row(
        Button(text="📦 Каталог", action="catalog"),
        Button(text="☎️ Зв'язатися з нами", action="contact_us"),
        Button(text="📱 Instagram, TikTok", action="social_media"),
    )

    kb.adjust(columns=3, rows=1, resize=True)
    return kb.to_dict()


def contact():
    kb = Keyboard()
    kb.add(Button(text="📞 Відправити мій номер телефону", action=" ", action_type="share-phone"))
    kb.resize_buttons(columns=3, rows=1)
    return kb.to_dict()