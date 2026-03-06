from celery import shared_task
import asyncio

from bot.tg_bot.utils import check_and_send_promo, scheduler_messages


@shared_task
def check_and_send_promo_task():
    asyncio.run(check_and_send_promo())

@shared_task
def scheduler_messages_task():
    asyncio.run(scheduler_messages())