# Колесо фортуни - Інструкція з налаштування

## Огляд

Реалізовано систему колеса фортуни для Telegram та Viber ботів з повною інтеграцією в існуючий проект.

## Що було зроблено

### Backend (Django)

1. **Моделі** (`miniapp/models.py`):
   - `WheelPrize` - призи з налаштуванням кольорів, ймовірностей та порядку
   - `WheelSpin` - історія прокрутів з підтримкою Telegram/Viber/анонімних користувачів

2. **API ендпоінти** (`miniapp/views.py`, `miniapp/urls.py`):
   - `GET /api/miniapp/wheel/prizes/` - список активних призів
   - `GET /api/miniapp/wheel/check-eligibility/` - перевірка можливості крутити
   - `POST /api/miniapp/wheel/spin/` - прокрутка колеса з розрахунком виграшу

3. **Адмін панель** (`miniapp/admin.py`):
   - Кастомний віджет для вибору кольору з візуальним превью (15 пастельних кольорів)
   - Управління призами та їх шансами
   - Перегляд історії прокрутів

### Frontend (React)

1. **Компонент** (`frontend/src/pages/BonusWheel.jsx`):
   - Повна копія функціоналу з test.html
   - Інтеграція з API
   - Підтримка Telegram WebApp та звичайного браузера

2. **Маршрутизація**:
   - `/miniapp/bonus-wheel` - сторінка колеса
   - Автоматичний редирект з Telegram `startapp=bonus_wheel`

3. **Стилі** (`frontend/src/pages/BonusWheel.css`):
   - Всі анімації збережено
   - Адаптивний дизайн

## Налаштування

### 1. Запуск міграцій

```bash
cd /home/malme/freelunce/freelunce/DlyaTebeBot/DlyaTebeBot
source venv/bin/activate
python manage.py migrate
```

### 2. Налаштування env змінних

**Backend** (`.env`):
```env
TELEGRAM_BOT_USERNAME=DLYA_TEBE_perfumes_bot
VIBER_CHAT_URI=your_viber_public_account_uri
```

**Frontend** (`frontend/.env`):
```env
VITE_TELEGRAM_BOT_USERNAME=DLYA_TEBE_perfumes_bot
VITE_VIBER_CHAT_URI=your_viber_public_account_uri
```

⚠️ **ВАЖЛИВО**: Замініть `your_viber_public_account_uri` на реальний chatURI вашого Viber Public Account.

### 3. Створення призів в адмінці

1. Зайдіть в Django admin: `/admin/`
2. Перейдіть в "Призи колеса фортуни"
3. Додайте призи (наприклад: "5 мл", "10 мл", "15 мл", "20 мл", "30 мл", "50 мл", "100 мл")
4. Для кожного призу:
   - Вкажіть ймовірність (в %) - сума всіх ймовірностей може бути будь-якою
   - Оберіть колір сектора з превью
   - Встановіть порядок на колесі (0-N)
   - Активуйте приз

### 4. Збірка фронтенду

```bash
cd /home/malme/freelunce/freelunce/DlyaTebeBot/DlyaTebeBot/frontend
npm run build
```

### 5. Collect static (якщо потрібно)

```bash
cd /home/malme/freelunce/freelunce/DlyaTebeBot/DlyaTebeBot
python manage.py collectstatic --noinput
```

## Використання

### Telegram

**Посилання на колесо:**
```
https://t.me/DLYA_TEBE_perfumes_bot/app?startapp=bonus_wheel
```

**Флоу:**
1. Користувач переходить за посиланням
2. Відкривається mini app з колесом
3. Авторизується автоматично через Telegram
4. Крутить колесо → виграш прив'язується до telegram_id
5. Натискає "Забрати приз" → переходить в бот з кодом: `https://t.me/bot?start={code}`

### Viber

**Посилання на колесо:**
```
https://your-domain.com/miniapp/bonus-wheel
```

**Флоу:**
1. Користувач сканує QR-код або переходить за посиланням
2. Відкривається в браузері
3. Крутить без авторизації → виграш зберігається в сесії
4. Натискає "Забрати приз" → переходить в Viber: `viber://pa?chatURI={uri}&context={code}`
5. Viber бот отримує код і прив'язує виграш до користувача

## Інтеграція з ботами

### Telegram бот

Додайте обробник для `start` команди з параметром:

```python
@router.message(CommandStart(deep_link=True))
async def handle_wheel_prize(message: Message, command: CommandObject):
    code = command.args
    
    if code and code.startswith('W'):
        # Перевірка та активація виграшу
        spin = WheelSpin.objects.filter(code=code, is_claimed=False).first()
        
        if spin:
            spin.tg_user = # поточний користувач
            spin.is_claimed = True
            spin.claimed_at = timezone.now()
            spin.save()
            
            await message.answer(
                f"🎉 Вітаємо! Ви виграли {spin.prize.name}!\n"
                f"Покажіть код на касі: {code}"
            )
```

### Viber бот

Обробка коду через `conversation_started` або звичайне повідомлення:

```python
def handle_wheel_prize(viber_user, code):
    if code and code.startswith('W'):
        spin = WheelSpin.objects.filter(code=code, is_claimed=False).first()
        
        if spin:
            spin.viber_user = viber_user
            spin.is_claimed = True
            spin.claimed_at = timezone.now()
            spin.save()
            
            return f"🎉 Вітаємо! Ви виграли {spin.prize.name}!\nПокажіть код на касі: {code}"
```

## Обмеження

- **1 спін на користувача** - реалізовано через перевірку в API
- **Throttling** - максимум 3 спроби на годину (захист від зловживань)
- **Код виграшу** - унікальний, генерується автоматично (формат: `W{random}`)

## Адмін панель

### Призи колеса фортуни
- Створення/редагування призів
- Налаштування ймовірностей (автоматичний розрахунок на основі вказаних %)
- Вибір кольору з 15 пастельних відтінків з візуальним превью
- Порядок відображення на колесі
- Перегляд кількості виграшів по кожному призу

### Прокрути колеса
- Історія всіх прокрутів
- Інформація про користувачів (Telegram/Viber/Анонімні)
- Статус виграшу (Очікує/Забрано)
- Фільтрація по датам та призам
- Пошук по коду або користувачу

## Troubleshooting

### Колесо не відображається
- Перевірте що міграції запущені
- Перевірте що є активні призи в адмінці
- Перевірте що фронтенд зібрано (`npm run build`)

### Виграш не прив'язується до користувача
- Telegram: перевірте що initData передається коректно
- Viber: перевірте що VIBER_CHAT_URI вказаний правильно

### Помилка "Ви вже крутили колесо"
- Це нормальна поведінка - 1 спін на користувача
- Для тестування видаліть записи з `WheelSpin` в адмінці

## Структура файлів

```
DlyaTebeBot/
├── miniapp/
│   ├── models.py              # WheelPrize, WheelSpin
│   ├── views.py               # API endpoints
│   ├── urls.py                # URL routing
│   ├── admin.py               # Admin configuration
│   ├── widgets.py             # ColorRadioSelect widget
│   ├── serializers.py         # API serializers
│   ├── templates/
│   │   └── admin/
│   │       └── widgets/
│   │           └── color_radio_select.html
│   └── static/
│       └── admin/
│           └── css/
│               └── color_radio_select.css
│
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── BonusWheel.jsx     # Компонент колеса
    │   │   └── BonusWheel.css     # Стилі
    │   ├── components/
    │   │   └── TelegramStartHandler.jsx  # Обробка startapp
    │   └── App.jsx                # Маршрутизація
    └── .env                       # Env змінні фронтенду
```

## API Endpoints

### GET `/api/miniapp/wheel/prizes/`
Отримати список активних призів для відображення на колесі.

**Response:**
```json
[
  {
    "id": 1,
    "name": "5 мл",
    "color": "#FFB5D8",
    "sort_order": 0
  }
]
```

### GET `/api/miniapp/wheel/check-eligibility/`
Перевірити чи може користувач крутити колесо.

**Response (може крутити):**
```json
{
  "can_spin": true,
  "already_spun": false
}
```

**Response (вже крутив):**
```json
{
  "can_spin": false,
  "already_spun": true,
  "prize": "10 мл",
  "code": "WABC123XYZ"
}
```

### POST `/api/miniapp/wheel/spin/`
Прокрутити колесо і отримати виграш.

**Request (опціонально):**
```json
{
  "session_key": "session_key_for_anonymous"
}
```

**Response:**
```json
{
  "id": 42,
  "code": "WABC123XYZ",
  "prize_name": "20 мл",
  "is_claimed": false,
  "created_at": "2026-07-21T10:30:00Z",
  "platform": "Telegram"
}
```

## Підтримка

При виникненні питань або проблем:
1. Перевірте логи Django: `docker logs dlyatebebot-backend`
2. Перевірте консоль браузера на помилки JavaScript
3. Перевірте що всі env змінні налаштовані правильно
