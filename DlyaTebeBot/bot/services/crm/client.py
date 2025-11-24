from __future__ import annotations

from datetime import date
from typing import Iterable, Optional

import requests
from django.conf import settings
from loguru import logger

from .schemas import Consumer, Purchase, RegisterFinishResponse


class ApiError(RuntimeError):
    """Represents an error that occurred while interacting with the CRM API."""

    pass


class CRMClient:
    """A client for interacting with the CRM API."""

    def __init__(
        self,
        phone: str,
        password: str,
        base_url: Optional[str] = None,
        timeout: int = 15,
    ):
        """Initializes the API client.

        Args:
            phone: The phone number to use for authentication.
            password: The password to use for authentication.
            base_url: The base URL of the CRM API.
            timeout: The timeout for API requests.
        """
        self.base_url = (base_url or settings.BASE_CRM_URL).rstrip("/") + "/"
        self.timeout = timeout

        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

        self.token: Optional[str] = None
        self._auth(phone, password)

    def _auth(self, phone: str, password: str) -> None:
        """Authenticates with the CRM API."""
        path = "api/v1/auth/"
        payload = {"phone": phone, "password": password}
        resp = self.session.post(
            self.base_url + path, json=payload, timeout=self.timeout
        )
        self._raise_for_status(resp)
        token = resp.json().get("token")
        if not token:
            raise ApiError("Auth succeeded but token is missing in response.")
        self.token = token
        self.session.headers.update({"Authorization": f"JWT {self.token}"})

    def _get(self, path: str, params: dict | None = None):
        """Sends a GET request to the CRM API."""
        resp = self.session.get(
            self.base_url + path.lstrip("/"), params=params, timeout=self.timeout
        )
        self._raise_for_status(resp)
        return resp

    def _post(self, path: str, json: dict | None = None):
        """Sends a POST request to the CRM API."""
        resp = self.session.post(
            self.base_url + path.lstrip("/"), json=json, timeout=self.timeout
        )
        self._raise_for_status(resp)
        return resp

    def _put(self, path: str, json: dict | None = None):
        """Sends a PUT request to the CRM API."""
        resp = self.session.put(
            self.base_url + path.lstrip("/"), json=json, timeout=self.timeout
        )
        self._raise_for_status(resp)
        return resp

    @staticmethod
    def _raise_for_status(resp: requests.Response) -> None:
        """Raises an `ApiError` if the response has an unsuccessful status code."""
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
        """Formats a phone number for use in a URL path."""
        phone = phone.strip().replace(" ", "")
        if phone.startswith("+"):
            phone = phone[1:]
        return phone

    @staticmethod
    def _format_date(v: date | str | None) -> Optional[str]:
        """Formats a date object as a string."""
        if v is None:
            return None
        if isinstance(v, date):
            return v.isoformat()
        return v

    def get_consumer_info(self, phone: str) -> Consumer:
        """Retrieves information about a consumer from the CRM."""
        phone_for_path = self._phone_for_profile_path(phone)
        path = f"api/v1/consumer/profile/{phone_for_path}"
        data = self._get(path).json()
        if "phone" not in data:
            data["phone"] = phone
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
        """Iterates over a consumer's purchases."""
        params = {
            "phone": phone,
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
            if not isinstance(data, list):
                raise ApiError(f"Unexpected purchases payload: {data!r}")

            batch = [Purchase.model_validate(x) for x in data]
            if not batch:
                break

            for item in batch:
                yield item

            if len(batch) < params["limit"]:
                break

            params["offset"] += params["limit"]

    def add_bonus(self, phone: str, amount: int) -> bool:
        """Adds bonus points to a consumer's account."""
        path = "api/v1/consumer/add_bonus"
        body = {"consumer_phone": phone, "bonus_amount": amount}
        resp = self._post(path, json=body)
        return resp.status_code == 201

    def create_consumer(
        self,
        phone: str,
        first_name: str,
        last_name: str,
        date_birth: date | str,
        gender: str,
    ) -> str:
        """Creates a new consumer in the CRM."""
        path = "api/v1/consumer/register/"
        body = {
            "phone": phone,
            "first_name": first_name,
            "last_name": last_name,
            "date_birth": (
                date_birth if isinstance(date_birth, str) else date_birth.isoformat()
            ),
            "gender": gender,
        }
        data = self._post(path, json=body).json()
        logger.info(f"Activation code received: {data}")
        return data.get("activation_code")

    def finish_registration(
        self, phone: str, activate_code: str
    ) -> RegisterFinishResponse:
        """Finishes the registration of a new consumer."""
        path = "api/v1/consumer/register/finish/"
        body = {"phone": phone, "activate_code": activate_code}
        data = self._put(path, json=body).json()
        result = RegisterFinishResponse.model_validate(data)
        result.user._client = self
        return result
