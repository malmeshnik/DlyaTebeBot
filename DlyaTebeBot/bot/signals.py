from loguru import logger

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .api import ApiCRM
from .models import TgUser

crm_client = ApiCRM(settings.PHONE_CRM_AUTH, settings.PASSWORD_CRM)

@receiver(post_save, sender=TgUser)
def check_CRM_consumer(sender, instance: TgUser, created: bool, **kwargs):
    """
    Checks if a newly created `TgUser` exists as a consumer in the CRM.
    If not, it creates a new consumer in the CRM.
    """
    if not created:
        return

    try:
        consumer = crm_client.get_consumer_info(instance.phone_number)
        logger.info(f"CRM consumer exists: #{consumer.id} ({consumer.phone})")
        return
    except (Exception) as e:
        logger.info(f"CRM consumer not found/invalid ({instance.phone_number}), will register. Reason: {e}")

    last_name = (instance.last_name or "Не знайдено").strip()
    date_birth = getattr(instance, "date_birth", None) or "2000-01-01"
    gender = getattr(instance, "gender", "") or ""

    validation_code = crm_client.create_consumer(
        phone=instance.phone_number,
        first_name=(instance.first_name or "").strip(),
        last_name=last_name,
        date_birth=str(date_birth),
        gender=gender,
    )
    register = crm_client.finish_registration(
        phone=instance.phone_number,
        activate_code=validation_code,
    )
    logger.info(f"Registered new consumer in CRM, bonus: {register.user.bonus}")