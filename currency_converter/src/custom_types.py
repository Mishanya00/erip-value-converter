from enum import Enum

from typing import NewType


class ExchangeStatus(Enum):
    PENDING = "pending"
    CANCELED = "canceled"
    CONFIRMED = "confirmed"


class ExchangeAction(Enum):
    CONFIRM = "confirm"
    CANCEL = "cancel"


Str3 = NewType("Str3", str)
Str128 = NewType("Str128", str)
