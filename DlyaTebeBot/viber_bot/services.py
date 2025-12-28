from typing import List, Optional, Any
from dataclasses import dataclass

from django.conf import settings
from viberbot.api.messages import TextMessage, PictureMessage, RichMediaMessage

from .keyboards import main_menu, contact
from .repo import ViberUserRepo, PromoCampaignRepo
from .utils import generate_qr_code
from .builders import PromoCardBuilder, PurchaseCardBuilder, SocialMediaBuilder
from .fsm import get_state, set_state, clear_state
from .constants import SOCIAL_MEDIA_URLS, BUTTON_COLORS
from bot.api import ApiCRM


@dataclass
class ViberService:
    repo: ViberUserRepo
    promo_repo: PromoCampaignRepo
    crm_client: ApiCRM

    def handle_start(self, user_id: str, user_name: str) -> List[TextMessage]:
        user, created = self.repo.update_or_create(user_id, name=user_name)
        if created:
            set_state(user_id, "contact")
            return [
                TextMessage(
                    text="Вітаю! Для продовження роботи відправте ваш номер телефону за допомогою кнопки 👇або введіть номер у форматі 380XXXXXXX",
                    keyboard=contact(),
                    min_api_version=6,
                )
            ]
        else:
            clear_state(user_id)
            return [
                TextMessage(
                    text="Ви в головному меню",
                    keyboard=main_menu(),
                    min_api_version=6,
                )
            ]

    def handle_contact(self, user_id: str, user_name: str, phone: str) -> List[TextMessage]:
        self.repo.update_or_create(user_id, name=user_name, phone_number=phone)
        clear_state(user_id)
        return [
            TextMessage(
                text=f"Дякую! Отримали номер: {phone}",
                keyboard=main_menu(),
                min_api_version=6,
            )
        ]

    def handle_bonus_card(self, user_id: str) -> List[PictureMessage]:
        phone = self.repo.get_phone(user_id)
        qr_url = generate_qr_code(phone)
        consumer = self.crm_client.get_consumer_info(phone)
        return [
            PictureMessage(
                text=f"QR-код для номера: {phone}. Бонусів: {consumer.bonus}",
                media=settings.VIBER_WEBHOOK_BASE_URL + qr_url,
                keyboard=main_menu(),
                min_api_version=6,
            )
        ]

    def handle_promo(self) -> List[RichMediaMessage]:
        builder = PromoCardBuilder()
        promos = self.promo_repo.get_active_campaigns()
        for promo in promos:
            builder.add_image_button(promo)
            builder.add_title_button(promo)
            builder.add_description_button(promo)
            builder.add_detail_button()
        return [
            RichMediaMessage(
                rich_media=builder.build_rich_media(),
                min_api_version=6,
                keyboard=main_menu(),
            )
        ]

    def handle_purchases(self, user_id: str) -> List[RichMediaMessage]:
        phone = self.repo.get_phone(user_id)
        consumer = self.crm_client.get_consumer_info(phone)
        if not consumer.purchaces:
            return [
                TextMessage(
                    text="У вас поки що немає покупок",
                    keyboard=main_menu(),
                    min_api_version=6,
                )
            ]
        builder = PurchaseCardBuilder()
        for purchase in consumer.purchaces:
            builder.add_header(purchase)
            builder.add_row("Сума:", f"{purchase.sum} грн", "sum", "sum_value")
            builder.add_row("Використано бонусів:", f"{purchase.bonus} грн", "bonus", "bonus_value")
            builder.add_row("Загалом", f"{purchase.total} грн", "total", "total_value")
            builder.add_detail_button(purchase.id)
        return [
            RichMediaMessage(
                rich_media=builder.build_rich_media(),
                min_api_version=6,
                keyboard=main_menu(),
            )
        ]

    def handle_social_media(self) -> List[RichMediaMessage]:
        builder = SocialMediaBuilder()
        builder.add_header()
        builder.add_spacer()
        builder.add_instagram_button()
        builder.add_spacer()
        builder.add_spacer()
        builder.add_tiktok_button()
        return [
            RichMediaMessage(
                rich_media=builder.build_rich_media(),
                keyboard=main_menu(),
                min_api_version=6,
            )
        ]

    def handle_contact_us(self) -> List[TextMessage]:
        return [
            TextMessage(
                text="Наші контакти: ",
                keyboard=main_menu(),
                min_api_version=6,
            )
        ]

    def handle_default(self) -> List[TextMessage]:
        return [
            TextMessage(
                text="Головне меню",
                keyboard=main_menu(),
                min_api_version=6,
            )
        ]