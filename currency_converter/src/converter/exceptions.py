from fastapi import status, HTTPException

from src.exceptions import BaseAppException



class ExternalAPIRequestError(BaseAppException):
    """Exception raised when there is an error while retrieving data from National bank API"""
    def __init__(self, message: str = "Error when requesting data from National Bank API"):
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE)