from random import randint

from aiogram import F, Router
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from django.conf import settings
from loguru import logger

from bot.services.crm.client import CRMClient
from bot.tg_bot.repo import TgUserRepo

router = Router()
tg_user_repo = TgUserRepo()
crm_client = CRMClient(settings.PHONE_CRM_AUTH, settings.PASSWORD_CRM)


@router.inline_query(F.query.startswith("promo"))
async def promo(query: InlineQuery):
    """Handles the inline query for promotions."""
    results = [
        InlineQueryResultArticle(
            id="promo",
            title="🎁 АКЦІЇ",
            description="Для повного перегляду акції виберіть її",
            thumbnail_url="https://upload.wikimedia.org/wikipedia/commons/5/59/Empty.png",
            input_message_content=InputTextMessageContent(
                message_text="main_menu",
            ),
        ),
    ]
    promocampaigns = await tg_user_repo.get_promocampaigns()
    if not promocampaigns:
        results = [
            InlineQueryResultArticle(
                id="a1",
                title="🎁 АКЦІЇ",
                description="Поки що немає активних акцій",
                thumbnail_url="https://upload.wikimedia.org/wikipedia/commons/5/59/Empty.png",
                input_message_content=InputTextMessageContent(
                    message_text="main_menu",
                ),
            ),
        ]

    logger.info(f"Found {len(promocampaigns)} promo")

    for promo_campaign in promocampaigns:
        desc = (promo_campaign.description or "")[:512]

        results.append(
            InlineQueryResultArticle(
                id=f"promo-{promo_campaign.id}",
                thumbnail_url=promo_campaign.image_url,
                title=promo_campaign.name,
                description=desc,
                input_message_content=InputTextMessageContent(
                    message_text=f"promo:{promo_campaign.id}",
                ),
            )
        )

    await query.answer(results=results, cache_time=1, is_personal=True)


@router.inline_query(F.query.startswith("my_purchases"))
async def inline_my_purchases(query: InlineQuery):
    """Handles the inline query for user purchases."""
    user_phone = await tg_user_repo.get_user_phone(query.from_user.id)
    consumer = crm_client.get_consumer_info(user_phone)

    results = [
        InlineQueryResultArticle(
            id="my_purchases",
            title="Мої покупки",
            description="Тут відображаються останні 5 ваших покупок",
            thumbnail_url="https://upload.wikimedia.org/wikipedia/commons/5/59/Empty.png",
            input_message_content=InputTextMessageContent(
                message_text="main_menu",
            ),
        )
    ]

    if not consumer.purchases:
        results.append(
            InlineQueryResultArticle(
                id="None-purchase",
                title="Ви ще не зробили жодної покупки 😔",
                description="Натисніть на це меню щоб відкрити наш каталог 🤗",
                thumbnail_url="https://upload.wikimedia.org/wikipedia/commons/5/59/Empty.png",
                input_message_content=InputTextMessageContent(
                    message_text="catalog",
                ),
            )
        )

    for purchase in consumer.purchases:
        for product in purchase.products:
            if not product.product.isdigit():
                results.append(
                    InlineQueryResultArticle(
                        id=f"purchase-{randint(1, 10000)}",
                        title=product.product,
                        description=f"Кількість: {product.quantity} Вартість: {product.price}",
                        thumbnail_url="https://upload.wikimedia.org/wikipedia/commons/5/59/Empty.png",
                        input_message_content=InputTextMessageContent(
                            message_text="main_menu",
                        ),
                    )
                )

    await query.answer(results=results, cache_time=1, is_personal=True)
