from __future__ import annotations

from typing import Optional, List, Iterable, Literal
from datetime import date, datetime
from decimal import Decimal
import requests

from pydantic import BaseModel, Field, PrivateAttr, field_validator
from django.conf import settings


# =========================
# Pydantic models
# =========================

class PurchaseProduct(BaseModel):
    product: str
    quantity: int
    price: Decimal  # у відповіді як рядок — парситься у Decimal


class Purchase(BaseModel):
    id: int
    date: datetime  # у відповіді "27-10-2025" -> парсимо у datetime
    promo: Optional[str] = None
    sum: Decimal = Decimal("0")
    bonus: int = 0
    total: Decimal = Decimal("0")
    products: List[PurchaseProduct] = Field(default_factory=list)

    @field_validator("date", mode="before")
    @classmethod
    def _parse_dd_mm_yyyy(cls, v):
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            # формат з прикладу: "27-10-2025"
            return datetime.strptime(v, "%d-%m-%Y")
        raise TypeError("Unsupported date type")

    @field_validator("sum", "total", mode="before")
    @classmethod
    def _to_decimal(cls, v):
        if v is None:
            return Decimal("0")
        if isinstance(v, (int, float, Decimal)):
            return Decimal(str(v))
        if isinstance(v, str):
            return Decimal(v)
        raise TypeError("Unsupported money type")


class Consumer(BaseModel):
    id: Optional[int] = None
    phone: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_birth: Optional[date | str] = None  # бек повертає "YYYY-MM-DD"
    gender: Optional[Literal["male", "female", "other", ""] | str] = None
    city: Optional[int] = None
    bonus: Optional[int] = 0

    # приватні поля — не серіалізуються
    _client: "ApiCRM" = PrivateAttr()
    _purchases_cache: Optional[List[Purchase]] = PrivateAttr(default=None)

    # Лінива властивість без фільтрів дат
    @property
    def purchases(self) -> List[Purchase]:
        if self._purchases_cache is None:
            self._purchases_cache = list(
                self._client.iter_consumer_purchases(self.phone)
            )
        return self._purchases_cache

    # Alias, якщо звик до помилкового написання
    @property
    def purchaces(self) -> List[Purchase]:
        return self.purchases

    def get_purchases(
        self,
        date_from: Optional[date | str] = None,
        date_to: Optional[date | str] = None,
        limit_per_page: int = 1000,
    ) -> List[Purchase]:
        """Отримати покупки з фільтрами дат (не кешується)."""
        return list(
            self._client.iter_consumer_purchases(
                self.phone, date_from=date_from, date_to=date_to, limit=limit_per_page
            )
        )

    def refresh(self) -> "Consumer":
        fresh = self._client.get_consumer_info(self.phone)
        for field in self.model_fields:
            setattr(self, field, getattr(fresh, field))
        self._purchases_cache = None
        return self


class RegisterFinishResponse(BaseModel):
    token: str
    user: Consumer


# =========================
# HTTP client
# =========================

class ApiError(RuntimeError):
    pass


class ApiCRM:
    def __init__(self, phone: str, password: str, base_url: Optional[str] = None, timeout: int = 15):
        self.base_url = (base_url or settings.BASE_CRM_URL).rstrip("/") + "/"
        self.timeout = timeout

        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

        self.token: Optional[str] = None
        self._auth(phone, password)

    # ---------- low-level ----------
    def _auth(self, phone: str, password: str) -> None:
        path = "api/v1/auth/"
        payload = {"phone": phone, "password": password}
        resp = self.session.post(self.base_url + path, json=payload, timeout=self.timeout)
        self._raise_for_status(resp)
        token = resp.json().get("token")
        if not token:
            raise ApiError("Auth succeeded but token is missing in response.")
        self.token = token
        self.session.headers.update({"Authorization": f"JWT {self.token}"})

    def _get(self, path: str, params: dict | None = None):
        resp = self.session.get(self.base_url + path.lstrip("/"), params=params, timeout=self.timeout)
        self._raise_for_status(resp)
        return resp

    def _post(self, path: str, json: dict | None = None):
        resp = self.session.post(self.base_url + path.lstrip("/"), json=json, timeout=self.timeout)
        self._raise_for_status(resp)
        return resp

    def _put(self, path: str, json: dict | None = None):
        resp = self.session.put(self.base_url + path.lstrip("/"), json=json, timeout=self.timeout)
        self._raise_for_status(resp)
        return resp

    @staticmethod
    def _raise_for_status(resp: requests.Response) -> None:
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            detail = None
            try:
                body = resp.json()
                detail = body.get("detail") or body
            except Exception:
                detail = resp.text[:500]
            raise ApiError(f"HTTP {resp.status_code}: {detail}") from e

    @staticmethod
    def _phone_for_profile_path(phone: str) -> str:
        """Профіль в path приймає номер БЕЗ '+'. """
        phone = phone.strip().replace(" ", "")
        if phone.startswith("+"):
            phone = phone[1:]
        return phone

    @staticmethod
    def _format_date(v: date | str | None) -> Optional[str]:
        if v is None:
            return None
        if isinstance(v, date):
            return v.isoformat()
        return v  # очікується "YYYY-MM-DD"

    # ---------- public API ----------
    def get_consumer_info(self, phone: str) -> Consumer:
        phone_for_path = self._phone_for_profile_path(phone)
        path = f"api/v1/consumer/profile/{phone_for_path}"
        data = self._get(path).json()
        if "phone" not in data:
            data["phone"] = phone  # збережемо оригінальний формат
        consumer = Consumer.model_validate(data)
        consumer._client = self
        return consumer

    def iter_consumer_purchases(
        self,
        phone: str,
        date_from: Optional[date | str] = None,
        date_to: Optional[date | str] = None,
        offset: int = 0,
        limit: int = 1000,
    ) -> Iterable[Purchase]:
        """
        Генератор покупок. Параметри:
          - phone — можна в форматі +380..., 380..., 0...
          - date_from/date_to — опційно, формат YYYY-MM-DD або date
          - offset/limit — пагінація бекенду (offset відносно останнього запису згідно специфікації)
        """
        params = {
            "phone": phone,  # бек приймає +380 / 380 / 063 — віддаємо як є
            "offset": max(0, int(offset)),
            "limit": max(1, int(limit)),
        }
        df = self._format_date(date_from)
        dt = self._format_date(date_to)
        if df:
            params["date_from"] = df
        if dt:
            params["date_to"] = dt

        while True:
            data = self._get("api/v1/consumer/purchase/list", params=params).json()
            # бек може віддати список без count — обробляємо напряму
            if not isinstance(data, list):
                # якщо раптом інший формат — кинемо помилку з дебагом
                raise ApiError(f"Unexpected purchases payload: {data!r}")

            batch = [Purchase.model_validate(x) for x in data]
            if not batch:
                break

            for item in batch:
                yield item

            # якщо повернув рівно limit — пробуємо наступну сторінку
            if len(batch) < params["limit"]:
                break

            params["offset"] += params["limit"]

    def add_bonus(self, phone: str, amount: int) -> bool:
        path = "api/v1/consumer/add_bonus"
        body = {"consumer_phone": phone, "bonus_amount": amount}
        resp = self._post(path, json=body)
        return resp.status_code == 201  # за специфікацією

    def create_consumer(
        self,
        phone: str,
        first_name: str,
        last_name: str,
        date_birth: date | str,
        gender: str,
    ) -> str:
        """
        Return activation code
        """
        path = "api/v1/consumer/register/"
        body = {
            "phone": phone,
            "first_name": first_name,
            "last_name": last_name,
            "date_birth": date_birth if isinstance(date_birth, str) else date_birth.isoformat(),
            "gender": gender,
        }
        data = self._post(path, json=body).json()
        # якщо бек не повертає профіль — зберемо мінімальний
        return data.get("activate_code")

    def finish_registration(self, phone: str, activate_code: str) -> RegisterFinishResponse:
        """
        PUT /api/v1/consumer/register/finish/
        Повертає { token, user }
        """
        path = "api/v1/consumer/register/finish/"
        body = {"phone": phone, "activate_code": activate_code}
        data = self._put(path, json=body).json()
        result = RegisterFinishResponse.model_validate(data)
        # прив’яжемо клієнт до поверненого користувача
        result.user._client = self
        return result


# =========================
# Приклад використання
# =========================
if __name__ == "__main__":
    # логін під наданим юзером (супервізор)
    client = ApiCRM("+380632734275", "TestPassword123")

    # профіль (у path номер без "+")
    consumer = client.get_consumer_info("+380681404382")
    print(consumer)

    # покупки БЕЗ фільтрів — через властивість (закешує):
    all_purchases = consumer.purchases
    print("Total cached purchases:", len(all_purchases))

    # покупки З фільтрами дат (без кешу):
    ranged = consumer.get_purchases(date_from="2020-12-29", date_to="2025-12-30", limit_per_page=500)
    print("Ranged purchases:", len(ranged))

    # бонуси:
    ok = client.add_bonus("+380681404382", 100)
    print("Bonus added:", ok)

    # реєстрація нового:
    # new_user = client.create_consumer("+380972040614", "fn", "ln", "2000-12-24", "female")
    # finish = client.finish_registration("+380972040614", "1111")
    # print("New token:", finish.token)
    # print("New user bonus:", finish.user.bonus)
