class BaseAppException(Exception):
    """Base service-layer exception in the app. All others should inherit from it"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class InternalServerException(BaseAppException):
    """Base service-layer exception in the app. It should be used for status code 500"""

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message, status_code)
