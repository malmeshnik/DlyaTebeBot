from django.utils import timezone
from asgiref.sync import sync_to_async

from .models import PromoCampaign, Message, BroadcastMessage


class PromoCampaignRepo:
    def get_active_campaigns(self):
        today = timezone.now().date()
        return list(
            PromoCampaign.objects.filter(start_date__lte=today, end_date__gte=today)
        )
    
    async def aget_active_campaigns(self):
        return await sync_to_async(self.get_active_campaigns)()
    
    def get_promo(self, pk: int) -> PromoCampaign | None:
        try:
            return PromoCampaign.objects.get(pk=pk)
        except PromoCampaign.DoesNotExist:
            return None
        
    async def aget_promo(self, pk: int) -> PromoCampaign | None:
        return await sync_to_async(self.get_promo)(pk)


class MessageRepo:
    def get_message_by_name(self, name: str) -> Message | None:
        try:
            return Message.objects.get(name=name)
        except Message.DoesNotExist:
            return None

    async def aget_message_by_name(self, name: str) -> Message | None:
        return await sync_to_async(self.get_message_by_name)(name)
    
    def get_text(self, name: str) -> str | None:
        message = self.get_message_by_name(name)
        if message:
            return message.text
        return None
    
    async def aget_text(self, name: str) -> str | None:
        return await sync_to_async(self.get_text)(name)
    
    def get_viber_text(self, name: str) -> str | None:
        message = self.get_message_by_name(name)
        if message:
            return message.strip_html()
        return None


class BroadCastMessageRepo:
    @staticmethod
    def get_ready_messages(self) -> list[BroadcastMessage]:
        now = timezone.now()
        qs = BroadcastMessage.objects.filter(scheduled_at__lte=now, send=False)
        return list(qs)

    async def aget_ready_messages(self) -> list[BroadcastMessage]:
        return await sync_to_async(self.get_ready_messages)()
