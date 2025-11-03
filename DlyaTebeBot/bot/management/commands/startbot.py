import os
import asyncio

from django.conf import settings
from django.core.management.base import BaseCommand
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from common.logging_setup import setup_logger
from bot.tg_bot import handlers

logger = setup_logger()

class Command(BaseCommand):
    help = "Starts the Telegram bot."

    def handle(self, *args, **kwargs):
        asyncio.run(main())

async def main():
    default = DefaultBotProperties(parse_mode="HTML")
    bot = Bot(token=settings.BOT_TOKEN, default=default)
    dp = Dispatcher()
    dp.include_router(handlers.router)
    logger.info("Starting bot polling...")
    await dp.start_polling(bot)