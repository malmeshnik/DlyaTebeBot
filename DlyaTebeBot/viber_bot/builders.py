from typing import List, Dict, Any

from .keyboards import Button
from .models import PromoCampaign
from bot.api import Purchase
from .constants import BUTTON_COLORS, SOCIAL_MEDIA_URLS
from django.conf import settings


class PromoCardBuilder:
    def __init__(self):
        self.buttons: List[Button] = []

    def add_image_button(self, promo: PromoCampaign) -> None:
        self.buttons.append(
            Button(
                rows=3,
                image=promo.image_url,
                bg_color=BUTTON_COLORS["default"],
                action_type="reply",
                action_body="photo",
            )
        )

    def add_title_button(self, promo: PromoCampaign) -> None:
        self.buttons.append(
            Button(
                rows=1,
                text=f"<b>{promo.name}</b>",
                text_size="large",
                action_type="reply",
                action_body="title",
                border_color=BUTTON_COLORS["default"],
            )
        )

    def add_description_button(self, promo: PromoCampaign) -> None:
        self.buttons.append(
            Button(
                rows=2,
                text=promo.description,
                action_type="reply",
                action_body="desc",
                border_color=BUTTON_COLORS["default"],
            )
        )

    def add_detail_button(self) -> None:
        self.buttons.append(
            Button(
                rows=1,
                text="Деталі",
                action_type="reply",
                action_body="click",
                border_color=BUTTON_COLORS["default"],
                bg_color=BUTTON_COLORS["accent"],
                text_h_align="center",
            )
        )

    def build_rich_media(self) -> Dict[str, Any]:
        kb_buttons = [btn.to_dict() for btn in self.buttons]
        return {
            "Type": "rich_media",
            "ButtonsGroupColumns": 6,
            "ButtonsGroupRows": 7,
            "BgColor": BUTTON_COLORS["default"],
            "Buttons": kb_buttons,
        }


class PurchaseCardBuilder:
    def __init__(self):
        self.buttons: List[Button] = []

    def add_header(self, purchase: Purchase) -> None:
        self.buttons.append(
            Button(
                text=f"Чек за {purchase.date}",
                text_size="large",
                action_type="reply",
                action_body="purchase_header",
                border_color=BUTTON_COLORS["default"],
            )
        )

    def add_row(self, label: str, value: str, label_action: str, value_action: str) -> None:
        self.buttons.append(
            Button(
                columns=4,
                text=label,
                text_h_align="left",
                border_color=BUTTON_COLORS["default"],
                action_type="reply",
                action_body=label_action,
            )
        )
        self.buttons.append(
            Button(
                columns=2,
                text=value,
                text_h_align="right",
                border_color=BUTTON_COLORS["default"],
                action_type="reply",
                action_body=value_action,
            )
        )

    def add_detail_button(self, purchase_id: int) -> None:
        self.buttons.append(
            Button(
                text="Переглянути деталі",
                action_type="reply",
                action_body=f"details_{purchase_id}",
                border_color=BUTTON_COLORS["default"],
                bg_color=BUTTON_COLORS["accent"],
                text_h_align="center",
            )
        )

    def build_rich_media(self) -> Dict[str, Any]:
        kb_buttons = [btn.to_dict() for btn in self.buttons]
        return {
            "Type": "rich_media",
            "ButtonsGroupColumns": 6,
            "ButtonsGroupRows": 5,
            "BgColor": BUTTON_COLORS["default"],
            "Buttons": kb_buttons,
        }


class SocialMediaBuilder:
    def __init__(self):
        self.buttons: List[Dict[str, Any]] = []

    def add_header(self) -> None:
        self.buttons.append({
            "Columns": 5,
            "Rows": 2,
            "BgColor": BUTTON_COLORS["default"],
            "Text": "<b>Наші соцмережі</b>",
            "ActionType": "none",
            "TextSize": "medium",
            "BorderColor": BUTTON_COLORS["default"],
            "ActionBody": "",
            "Silent": True,
        })

    def add_spacer(self) -> None:
        self.buttons.append({
            "Columns": 1,
            "Rows": 1,
            "BgColor": BUTTON_COLORS["default"],
            "Text": "",
            "ActionType": "none",
            "BorderColor": BUTTON_COLORS["default"],
            "ActionBody": "",
            "Silent": True,
        })

    def add_instagram_button(self) -> None:
        self.buttons.append({
            "Text": "<b>Instagram</b>",
            "Columns": 3,
            "Rows": 1,
            "TextSize": "large",
            "ActionType": "open-url",
            "ActionBody": SOCIAL_MEDIA_URLS["instagram"],
            "BorderColor": BUTTON_COLORS["default"],
            "Image": settings.VIBER_WEBHOOK_BASE_URL + "/media/viber/buttons/insta.png",
            "Silent": True,
        })

    def add_tiktok_button(self) -> None:
        self.buttons.append({
            "Text": "TikTok",
            "Columns": 3,
            "Rows": 1,
            "BgColor": BUTTON_COLORS["accent"],
            "TextColor": BUTTON_COLORS["default"],
            "TextSize": "large",
            "ActionType": "open-url",
            "ActionBody": SOCIAL_MEDIA_URLS["tiktok"],
            "BorderColor": BUTTON_COLORS["default"],
            "TextVAlign": "middle",
            "CornerRadius": 10,
            "Silent": True,
        })

    def build_rich_media(self) -> Dict[str, Any]:
        return {
            "Type": "rich_media",
            "ButtonsGroupColumns": 5,
            "ButtonsGroupRows": 4,
            "BgColor": BUTTON_COLORS["default"],
            "Buttons": self.buttons,
        }