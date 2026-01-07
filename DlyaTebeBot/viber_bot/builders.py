from typing import List, Dict, Any
from dataclasses import dataclass, field

from django.conf import settings

from bot.api import Purchase
from bots_settings.models import PromoCampaign
from .keyboards import Button
from .constants import BUTTON_COLORS, SOCIAL_MEDIA_URLS


@dataclass
class PromoCardBuilder:
    buttons: List[Button] = field(default_factory=list)

    def add_promo_buttons(self, promo: PromoCampaign) -> 'PromoCardBuilder':
        """Add all buttons for a promo in one call."""
        self.buttons.extend([
            Button(
                rows=3,
                image=promo.image_url,
                bg_color=BUTTON_COLORS["default"],
                action_type="reply",
                action_body="photo",
            ),
            Button(
                rows=1,
                text=f"<b>{promo.name}</b>",
                text_size="large",
                action_type="reply",
                action_body="title",
                border_color=BUTTON_COLORS["default"],
            ),
            Button(
                rows=2,
                text=promo.description,
                action_type="reply",
                action_body="desc",
                border_color=BUTTON_COLORS["default"],
            ),
            Button(
                rows=1,
                text="Деталі",
                action_type="reply",
                action_body=f"promo_{promo.id}",
                border_color=BUTTON_COLORS["default"],
                bg_color=BUTTON_COLORS["accent"],
                text_h_align="center",
            ),
        ])
        return self

    def build_rich_media(self) -> Dict[str, Any]:
        kb_buttons = [btn.to_dict() for btn in self.buttons]
        return {
            "Type": "rich_media",
            "ButtonsGroupColumns": 6,
            "ButtonsGroupRows": 7,
            "BgColor": BUTTON_COLORS["default"],
            "Buttons": kb_buttons,
        }


# Factory function for simplicity
def create_promo_rich_media(promos: List[PromoCampaign]) -> Dict[str, Any]:
    builder = PromoCardBuilder()
    for promo in promos:
        builder.add_promo_buttons(promo)
    return builder.build_rich_media()


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