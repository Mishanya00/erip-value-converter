from fastapi import status

from src.exceptions import BaseAppException


class ExternalAPIRequestError(BaseAppException):
    """Exception raised when there is an error while retrieving data from National bank API"""

    def __init__(
        self, message: str = "Error when requesting data from National Bank API"
    ):
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE)


class CurrencyNotSpecifiedError(BaseAppException):
    """Exception raised when source or target currency is not specified"""

    def __init__(self, message: str = "Source or target currency not specified!"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class CurrencyAmountNotSpecifiedError(BaseAppException):
    """Exception raised when source currency amount is not specified"""

    def __init__(self, message: str = "Source currency amount not specified!"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class CurrencyAmountInvalidValueError(BaseAppException):
    """Exception raised when source currency amount is less than or equal to zero"""

    def __init__(self, message: str = "Invalid source currency amount!"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class IdenticalCurrenciesSpecifiedError(BaseAppException):
    """Exception raised when source and target currencies are equal"""

    def __init__(self, message: str = "Source and target currencies are identical!"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class CurrencyDoesNotExistError(BaseAppException):
    """Exception raised when currency does not exist"""

    def __init__(self, message: str = "Currency does not exist!"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)
