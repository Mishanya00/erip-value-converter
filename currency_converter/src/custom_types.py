from enum import Enum


class ExchangeStatus(Enum):
    PENDING = "pending"
    CANCELED = "canceled"
    CONFIRMED = "confirmed"
