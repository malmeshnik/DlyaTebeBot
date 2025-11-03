import os
import asyncio

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from common.logging_setup import setup_logger
from . import handlers

logger = setup_logger()

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def main():
    default = DefaultBotProperties(parse_mode="HTML")
    bot = Bot(token=BOT_TOKEN, default=default)
    dp = Dispatcher(default=default)
    dp.include_router(handlers.router)
    logger.info("Starting bot polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())