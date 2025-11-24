import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from django.conf import settings
from django.core.management.base import BaseCommand

from bot.tg_bot import handlers
from common.logging_setup import setup_logger

logger = setup_logger()


class Command(BaseCommand):
    """Starts the Telegram bot."""

    help = "Starts the Telegram bot."

    def handle(self, *args, **kwargs):
        """Handles the command."""
        asyncio.run(main())


async def main():
    """The main function that starts the bot."""
    default = DefaultBotProperties(parse_mode="HTML")
    bot = Bot(token=settings.BOT_TOKEN, default=default)
    dp = Dispatcher()
    dp.include_router(handlers.router)
    logger.info("Starting bot polling...")
    await dp.start_polling(bot)
