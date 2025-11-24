from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, PrivateAttr, field_validator


class PurchaseProduct(BaseModel):
    """Represents a product in a purchase."""
    product: str
    quantity: int
    price: float
    external_id: str | None = None


class Purchase(BaseModel):
    """Represents a purchase made by a consumer."""
    id: int
    date: datetime
    promo: Optional[str] = None
    sum: Decimal = Decimal("0")
    bonus: int = 0
    total: Decimal = Decimal("0")
    products: List[PurchaseProduct] = Field(default_factory=list)

    @field_validator("date", mode="before")
    @classmethod
    def _parse_dd_mm_yyyy(cls, v):
        """Parses a date string in DD-MM-YYYY format."""
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            return datetime.strptime(v, "%d-%m-%Y")
        raise TypeError("Unsupported date type")

    @field_validator("sum", "total", mode="before")
    @classmethod
    def _to_decimal(cls, v):
        """Converts a value to a `Decimal`."""
        if v is None:
            return Decimal("0")
        if isinstance(v, (int, float, Decimal)):
            return Decimal(str(v))
        if isinstance(v, str):
            return Decimal(v)
        raise TypeError("Unsupported money type")


class Consumer(BaseModel):
    """Represents a consumer in the CRM."""
    id: Optional[int] = None
    phone: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_birth: Optional[date | str] = None
    gender: Optional[Literal["male", "female", "other", ""] | str] = None
    city: Optional[int] = None
    bonus: Optional[int] = 0

    _client: "CRMClient" = PrivateAttr()
    _purchases_cache: Optional[List[Purchase]] = PrivateAttr(default=None)

    @property
    def purchases(self) -> List[Purchase]:
        """A list of the consumer's purchases."""
        if self._purchases_cache is None:
            self._purchases_cache = list(
                self._client.iter_consumer_purchases(self.phone)
            )
        return self._purchases_cache

    def get_purchases(
        self,
        date_from: Optional[date | str] = None,
        date_to: Optional[date | str] = None,
        limit_per_page: int = 1000,
    ) -> List[Purchase]:
        """Retrieves a list of purchases with optional date filters."""
        return list(
            self._client.iter_consumer_purchases(
                self.phone, date_from=date_from, date_to=date_to, limit=limit_per_page
            )
        )

    def refresh(self) -> "Consumer":
        """Refreshes the consumer's data from the CRM."""
        fresh = self._client.get_consumer_info(self.phone)
        for field in self.model_fields:
            setattr(self, field, getattr(fresh, field))
        self._purchases_cache = None
        return self


class RegisterFinishResponse(BaseModel):
    """Represents the response from the registration finish endpoint."""
    token: str
    user: Consumer
