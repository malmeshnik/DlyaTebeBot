from datetime import timedelta

from celery import shared_task
from django.utils import timezone
from django.conf import settings

from .repo import ViberUserRepo
from .service.broadcast import broadcast
from bots_settings.repo import PromoCampaignRepo, MessageRepo, BroadCastMessageRepo

@shared_task
def check_and_send_promo_task():
    today = timezone.localdate()

    promo_campaigns = PromoCampaignRepo.get_active_campaigns()

    for promo in promo_campaigns:
        start = promo.start_date
        end = promo.end_date

        if start == today:
            msg = MessageRepo.get_message_by_name("start_promo")
        elif promo.end_date == today:
            msg = MessageRepo.get_message_by_name("end_promo")
        elif promo.end_date - timedelta(days=3) == today:
            msg = MessageRepo.get_message_by_name("before_end_promo")
        else:
            continue

        msg_text = msg.text.format(name_promo=promo.name, name="")

        broadcast(msg_text)

@shared_task
def scheduler_messages_task():
    ready_messages = BroadCastMessageRepo.get_ready_messages()

    for msg in ready_messages:
        if msg.image.exists():
            broadcast(msg.text, settings.DOMAIN + msg.image.url)
        
        else:
            broadcast(msg.text)

        msg.send = True
        msg.save()