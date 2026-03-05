from typing import List, Optional, Any
from dataclasses import dataclass

from django.conf import settings
from viberbot.api.messages import TextMessage, PictureMessage, RichMediaMessage

from bot.api import ApiCRM
from bots_settings.repo import PromoCampaignRepo, MessageRepo
from .keyboards import main_menu, contact
from .repo import ViberUserRepo
from .utils import generate_qr_code
from .builders import PromoCardBuilder, PurchaseCardBuilder, SocialMediaBuilder
from .fsm import get_state, set_state, clear_state
from .repo import ViberMessageRepo


@dataclass
class ViberService:
    repo: ViberUserRepo
    promo_repo: PromoCampaignRepo
    crm_client: ApiCRM
    msg_repo: MessageRepo

    def handle_start(self, user_id: str, user_name: str) -> List[TextMessage]:
        user, created = self.repo.update_or_create(user_id, name=user_name)
        text = self.msg_repo.get_text("start")
        ViberMessageRepo.create(user=user, text=text, is_bot=True)

        if created:
            set_state(user_id, "contact")
            return [
                TextMessage(
                    text=text,
                    keyboard=contact(),
                    min_api_version=6,
                )
            ]
        else:
            clear_state(user_id)
            return [
                TextMessage(
                    text=text,
                    keyboard=main_menu(),
                    min_api_version=6,
                )
            ]

    def handle_contact(
        self, user_id: str, user_name: str, phone: str
    ) -> List[TextMessage]:
        user, _ = self.repo.update_or_create(user_id, name=user_name, phone_number=phone)
        clear_state(user_id)
        text = self.msg_repo.get_text("contact_received")
        ViberMessageRepo.create(user=user, text=text, is_bot=True)
        return [
            TextMessage(
                text=text,
                keyboard=main_menu(),
                min_api_version=6,
            )
        ]

    def handle_bonus_card(self, user_id: str) -> List[PictureMessage]:
        phone = self.repo.get_phone(user_id)
        qr_url = generate_qr_code(phone)
        consumer = self.crm_client.get_consumer_info(phone)
        text = self.msg_repo.get_viber_text("bonus_card").format(
            name=consumer.first_name, bonus=consumer.bonus
        )

        user, _ = self.repo.update_or_create(user_id)
        ViberMessageRepo.create(user=user, text=text, is_bot=True)

        return [
            PictureMessage(
                text=text,
                media=settings.VIBER_WEBHOOK_BASE_URL + qr_url,
                keyboard=main_menu(),
                min_api_version=6,
            )
        ]

    def handle_promo(self) -> List[RichMediaMessage]:
        promos = self.promo_repo.get_active_campaigns()

        if promos:
            builder = PromoCardBuilder()

            for promo in promos:
                builder.add_promo_buttons(promo)
            return [
                RichMediaMessage(
                    rich_media=builder.build_rich_media(),
                    min_api_version=6,
                    keyboard=main_menu(),
                )
            ]

        else:
            return [
                TextMessage(
                    text="Наразі немає активних акцій",
                    keyboard=main_menu(),
                    min_api_version=6,
                )
            ]

    def handle_promo_details(self, promo_id: int) -> List[PictureMessage]:
        promo = self.promo_repo.get_promo(promo_id)
        return [
            PictureMessage(
                text=f"{promo.name}\n\n{promo.description}",
                media=promo.image_url,
                keyboard=main_menu(),
                min_api_version=6,
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
        purchases = consumer.purchaces[-5:]
        builder = PurchaseCardBuilder()
        for purchase in purchases:
            builder.add_header(purchase)
            builder.add_row("Сума:", f"{purchase.sum} грн", "sum", "sum_value")
            builder.add_row(
                "Використано бонусів:", f"{purchase.bonus} грн", "bonus", "bonus_value"
            )
            builder.add_row("Загалом", f"{purchase.total} грн", "total", "total_value")
            builder.add_detail_button(purchase.id)
        return [
            RichMediaMessage(
                rich_media=builder.build_rich_media(),
                min_api_version=6,
                keyboard=main_menu(),
            )
        ]

    def handle_purchase_detail(
        self, user_id: str, purchase_id: int
    ) -> list[RichMediaMessage]:
        phone = self.repo.get_phone(user_id)
        consumer = self.crm_client.get_consumer_info(phone)
        purchase = next((p for p in consumer.purchaces if p.id == purchase_id), None)

        if not purchase:
            return [
                TextMessage(
                    text="Деталі покупки не знайдені.",
                    keyboard=main_menu(),
                    min_api_version=6,
                )
            ]

        builder = PurchaseCardBuilder()
        builder.add_row("<b>ТОВАР</b>", "<b>ГРН</b>", "header_product", "header_price")
        for product in purchase.products:
            product_name = (
                f"Парфюм {product.product}"
                if product.product.isdigit()
                else product.product
            )
            builder.add_row(
                f"{product.quantity} x {product_name}",
                f"{product.price}",
                f"product_{product.product}",
                f"price_{product.product}",
            )

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
                text=self.msg_repo.get_text("contact_request"),
                keyboard=main_menu(),
                min_api_version=6,
            )
        ]

    def handle_default(self, user_id: Optional[str] = None) -> List[TextMessage]:
        text = "Головне меню"
        if user_id:
            user, _ = self.repo.update_or_create(user_id)
            ViberMessageRepo.create(user=user, text=text, is_bot=True)
        return [
            TextMessage(
                text=text,
                keyboard=main_menu(),
                min_api_version=6,
            )
        ]
