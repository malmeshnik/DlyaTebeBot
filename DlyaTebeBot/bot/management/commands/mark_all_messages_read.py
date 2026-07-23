from django.core.management.base import BaseCommand
from bot.models import TgMessage
from viber_bot.models import ViberMessage


class Command(BaseCommand):
    help = 'Позначає всі існуючі повідомлення як прочитані'

    def handle(self, *args, **options):
        self.stdout.write('Позначаємо всі повідомлення як прочитані...')

        # Telegram повідомлення
        tg_updated = TgMessage.objects.filter(is_read=False).update(is_read=True)
        self.stdout.write(
            self.style.SUCCESS(f'✓ Telegram: позначено {tg_updated} повідомлень як прочитані')
        )

        # Viber повідомлення
        viber_updated = ViberMessage.objects.filter(is_read=False).update(is_read=True)
        self.stdout.write(
            self.style.SUCCESS(f'✓ Viber: позначено {viber_updated} повідомлень як прочитані')
        )

        total = tg_updated + viber_updated
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Всього позначено {total} повідомлень як прочитані')
        )
