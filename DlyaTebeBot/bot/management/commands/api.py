import os
import asyncio

from django.conf import settings
from django.core.management.base import BaseCommand
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from common.logging_setup import setup_logger
from bot.tg_bot import handlers
from bot.api import ApiCRM

logger = setup_logger()

class Command(BaseCommand):
    help = "Starts the Telegram bot."

    def handle(self, *args, **kwargs):
        api = ApiCRM("+380632734275", "TestPassword123")
        print(api.token)
        consumer = api.get_consumer_info("+380681404382")
        print(consumer)
        all_purchases = consumer.purchases
        print("Total cached purchases:", len(all_purchases))
        print(all_purchases)
        ok = api.add_bonus("+380681404382", 100)
        print("Bonus added:", ok)