# Тестування через ngrok

## Проблема
Коли відкриваєш фронтенд через ngrok на телефоні або іншому пристрої, він намагається звернутися до `localhost:8000`, який недоступний з цього пристрою.

## Рішення
Додано підтримку динамічного API URL через env змінну `VITE_API_BASE_URL`.

## Як використовувати

### Варіант 1: Локальна розробка (без ngrok)

**frontend/.env:**
```env
VITE_API_BASE_URL=
```

Залиш порожнім або не вказуй взагалі. Використовується proxy з vite.config.js.

**Запуск:**
```bash
# Terminal 1 - Backend
cd DlyaTebeBot
source venv/bin/activate
python manage.py runserver

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Відкривай: `http://localhost:5173/miniapp/bonus-wheel`

---

### Варіант 2: Тестування через ngrok

#### Крок 1: Запусти ngrok для backend

```bash
ngrok http 8000
```

Отримаєш URL типу: `https://92a6-89-105-225-214.ngrok-free.app`

#### Крок 2: Налаштуй frontend/.env

```env
VITE_API_BASE_URL=https://92a6-89-105-225-214.ngrok-free.app
```

#### Крок 3: Додай ngrok URL в Django ALLOWED_HOSTS

**DlyaTebeBot/.env:**
```env
ALLOWED_HOSTS=*,
CSRF_TRUSTED_ORIGINS=https://92a6-89-105-225-214.ngrok-free.app
CORS_ALLOWED_ORIGINS=https://92a6-89-105-225-214.ngrok-free.app
```

Або в `settings.py` додай:
```python
ALLOWED_HOSTS = ['92a6-89-105-225-214.ngrok-free.app', 'localhost', '127.0.0.1']
```

#### Крок 4: Зібери фронтенд

```bash
cd frontend
npm run build
```

#### Крок 5: Відкрий через ngrok

```
https://92a6-89-105-225-214.ngrok-free.app/miniapp/bonus-wheel
```

Тепер працюватиме на будь-якому пристрої! 📱

---

## Як це працює

### Локально (без env змінної)
```javascript
const API_BASE_URL = ''; // порожній
fetch(`${API_BASE_URL}/api/miniapp/wheel/prizes/`);
// => fetch('/api/miniapp/wheel/prizes/')
// => Vite proxy перенаправляє на http://localhost:8000/api/miniapp/wheel/prizes/
```

### Через ngrok (з env змінною)
```javascript
const API_BASE_URL = 'https://92a6-89-105-225-214.ngrok-free.app';
fetch(`${API_BASE_URL}/api/miniapp/wheel/prizes/`);
// => fetch('https://92a6-89-105-225-214.ngrok-free.app/api/miniapp/wheel/prizes/')
// => Прямий запит до backend через ngrok
```

---

## Варіант 3: Два ngrok тунелі (фронт + бек окремо)

Якщо хочеш окремий ngrok для фронтенду:

```bash
# Terminal 1 - Backend ngrok
ngrok http 8000

# Terminal 2 - Frontend ngrok  
ngrok http 5173

# Terminal 3 - Backend
python manage.py runserver

# Terminal 4 - Frontend dev
npm run dev
```

**frontend/.env:**
```env
VITE_API_BASE_URL=https://backend-ngrok-url.ngrok-free.app
```

Відкривай: `https://frontend-ngrok-url.ngrok-free.app/miniapp/bonus-wheel`

---

## Troubleshooting

### CORS помилка
Додай ngrok URL в `CORS_ALLOWED_ORIGINS` в Django settings.

### 404 Not Found на API
Перевір що `VITE_API_BASE_URL` містить правильний ngrok URL без `/` в кінці.

### Білий екран
1. Перевір консоль браузера (F12)
2. Перевір що backend запущений
3. Перевір що ngrok тунель активний
4. Перевір що env змінні встановлені правильно

### Після зміни .env нічого не працює
Перезапусти vite dev server (`npm run dev`) або перезбери проект (`npm run build`).

---

## Приклад повного workflow для тестування на телефоні

```bash
# 1. Запусти ngrok для backend
ngrok http 8000
# Отримаєш: https://abc123.ngrok-free.app

# 2. Встанови в frontend/.env
echo "VITE_API_BASE_URL=https://abc123.ngrok-free.app" > frontend/.env

# 3. Додай в backend .env
echo "CSRF_TRUSTED_ORIGINS=https://abc123.ngrok-free.app" >> DlyaTebeBot/.env

# 4. Запусти backend
cd DlyaTebeBot
source venv/bin/activate
python manage.py runserver

# 5. Зібери фронтенд
cd frontend
npm run build

# 6. Відкрий на телефоні
https://abc123.ngrok-free.app/miniapp/bonus-wheel
```

Готово! 🎉
