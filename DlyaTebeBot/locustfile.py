from locust import HttpUser, task, between

class BotLoadTest(HttpUser):
    wait_time = between(1, 3)  # Час між запитами: 1-3 сек

    @task
    def test_viber_webhook(self):
        # Виправлений payload для Viber webhook (згідно з документацією Viber)
        headers = {"Content-Type": "application/json"}
        payload = {
            "event": "message",
            "timestamp": 1234567890,
            "chat_hostname": "example.com",  # Додай, якщо потрібно
            "message_token": 123456789,
            "sender": {
                "id": "user123",
                "name": "Test User",
                "language": "uk",
                "country": "UA"
            },
            "message": {
                "type": "text",
                "text": "hello",
                "tracking_data": "tracking_data"
            }
        }
        self.client.post("/viber/webhook/", json=payload, headers=headers)

    @task(2)  # Цей task виконується вдвічі частіше
    def test_telegram_webhook(self):
        # Якщо є Telegram webhook (POST до /telegram/webhook/)
        # Payload для Telegram (якщо налаштовано)
        headers = {"Content-Type": "application/json"}
        payload = {
            "update_id": 123,
            "message": {
                "message_id": 456,
                "from": {"id": 123456, "first_name": "Test", "username": "testuser"},
                "chat": {"id": 123456, "type": "private"},
                "date": 1234567890,
                "text": "/start"
            }
        }
        self.client.post("/telegram/webhook/", json=payload, headers=headers)

    @task
    def test_django_admin(self):
        # Тест логіну в адмінку (якщо потрібно аутентифікація)
        self.client.get("/admin/")