import asyncio

from django.conf import settings
from django.core.management.base import BaseCommand
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from common.logging_setup import setup_logger
from bot.tg_bot.utils import check_and_send_promo, scheduler_messages

logger = setup_logger()


async def main():
    tz = getattr(settings, "TIME_ZONE", "Europe/Kyiv")

    scheduler = AsyncIOScheduler(timezone=tz)

    scheduler.add_job(
        check_and_send_promo,
        trigger="cron",
        hour=9,
        minute=0,
        id="check_and_send_promo_daily",
        replace_existing=True,
    )

    scheduler.add_job(
        scheduler_messages,
        trigger="interval",
        minutes=1,
        id="scheduler_messages_every_minute",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Schedulers started")

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stopping schedulers...")
        scheduler.shutdown()


class Command(BaseCommand):
    help = "Starts the Telegram bot schedulers."

    def handle(self, *args, **kwargs):
        logger.info("Starting schedulers command...")
        asyncio.run(main())
