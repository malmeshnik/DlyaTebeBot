# TODO: Наступні кроки для завершення інтеграції

## ✅ Що вже зроблено

- ✅ Backend моделі (WheelPrize, WheelSpin)
- ✅ API ендпоінти для колеса
- ✅ Адмін панель з кастомним віджетом для кольорів
- ✅ React компонент колеса фортуни
- ✅ Маршрутизація та обробка Telegram startapp параметра
- ✅ Міграція створена (потрібно застосувати)

## 🔧 Що потрібно зробити

### 1. Застосувати міграції ⚠️ ОБОВ'ЯЗКОВО

```bash
cd /home/malme/freelunce/freelunce/DlyaTebeBot/DlyaTebeBot
source venv/bin/activate
python manage.py migrate
```

### 2. Налаштувати Viber Chat URI

**Файл:** `DlyaTebeBot/.env`
```env
VIBER_CHAT_URI=ваш_реальний_viber_chat_uri
```

**Файл:** `frontend/.env`
```env
VITE_VIBER_CHAT_URI=ваш_реальний_viber_chat_uri
```

Замініть `your_viber_public_account_uri` на реальний chatURI з Viber Public Account.

### 3. Створити призи в адмінці

1. Запустіть сервер
2. Зайдіть в `/admin/`
3. "Призи колеса фортуни" → "Додати"
4. Створіть призи (наприклад):
   - 5 мл (ймовірність: 30%)
   - 10 мл (ймовірність: 25%)
   - 15 мл (ймовірність: 20%)
   - 20 мл (ймовірність: 15%)
   - 30 мл (ймовірність: 7%)
   - 50 мл (ймовірність: 2%)
   - 100 мл (ймовірність: 1%)

### 4. Збірка фронтенду

```bash
cd /home/malme/freelunce/freelunce/DlyaTebeBot/DlyaTebeBot/frontend
npm run build
```

### 5. Інтеграція з ботами

#### Telegram бот

Додайте обробник для активації призу по коду в `bot/tg_bot/handlers/`:

```python
from miniapp.models import WheelSpin
from django.utils import timezone

@router.message(CommandStart(deep_link=True))
async def handle_wheel_prize(message: Message, command: CommandObject):
    code = command.args
    
    if code and code.startswith('W'):
        try:
            spin = WheelSpin.objects.get(code=code, is_claimed=False)
            
            # Прив'язуємо до користувача
            tg_user = TgUserRepo.get_or_create(telegram_id=message.from_user.id)[0]
            spin.tg_user = tg_user
            spin.is_claimed = True
            spin.claimed_at = timezone.now()
            spin.save()
            
            await message.answer(
                f"🎉 Вітаємо!\n\n"
                f"Ви виграли: {spin.prize.name}\n"
                f"Ваш код: <code>{code}</code>\n\n"
                f"Покажіть цей код на касі магазину.",
                parse_mode="HTML"
            )
        except WheelSpin.DoesNotExist:
            await message.answer("❌ Невірний або вже використаний код.")
```

#### Viber бот

Додайте обробник в `viber_bot/handlers.py`:

```python
from miniapp.models import WheelSpin
from django.utils import timezone

def handle_wheel_code(viber_user, text):
    """Обробка коду виграшу з колеса"""
    if text and text.startswith('W'):
        try:
            spin = WheelSpin.objects.get(code=text, is_claimed=False)
            
            # Прив'язуємо до користувача
            spin.viber_user = viber_user
            spin.is_claimed = True
            spin.claimed_at = timezone.now()
            spin.save()
            
            return (
                f"🎉 Вітаємо!\n\n"
                f"Ви виграли: {spin.prize.name}\n"
                f"Ваш код: {text}\n\n"
                f"Покажіть цей код на касі магазину."
            )
        except WheelSpin.DoesNotExist:
            return "❌ Невірний або вже використаний код."
    return None

# Додайте цей виклик у відповідний handler
```

### 6. Тестування

#### Локально
1. Запустіть backend: `python manage.py runserver`
2. Запустіть frontend dev: `cd frontend && npm run dev`
3. Відкрийте `http://localhost:5173/miniapp/bonus-wheel`

#### Telegram Mini App
1. Використайте ngrok або інший тунель
2. Посилання: `https://t.me/DLYA_TEBE_perfumes_bot/app?startapp=bonus_wheel`

#### Viber
1. Створіть QR-код з посиланням: `https://your-domain.com/miniapp/bonus-wheel`
2. Роздрукуйте QR-коди для магазинів

## 📝 Корисні команди

### Видалити всі прокрути (для тестування)
```python
python manage.py shell
>>> from miniapp.models import WheelSpin
>>> WheelSpin.objects.all().delete()
```

### Перевірити кількість виграшів
```python
python manage.py shell
>>> from miniapp.models import WheelSpin
>>> WheelSpin.objects.values('prize__name').annotate(count=Count('id'))
```

### Перевірити незабрані призи
```python
python manage.py shell
>>> from miniapp.models import WheelSpin
>>> WheelSpin.objects.filter(is_claimed=False).count()
```

## 🐛 Очікувані проблеми

### "Ви вже крутили колесо" при тестуванні
**Рішення:** Видаліть записи WheelSpin для тестового користувача в адмінці

### Колесо не відображається
**Рішення:** 
- Перевірте міграції: `python manage.py showmigrations miniapp`
- Перевірте що є активні призи: `/admin/miniapp/wheelprize/`

### Помилка при спіні
**Рішення:** Перевірте логи Django і консоль браузера

## 📚 Додаткова документація

Детальна документація в файлі: `WHEEL_SETUP.md`
