"""
======
Errors
======
This module holds exceptions for all other app
"""

from rest_framework import exceptions, status


class ErrorMessage:
    UNEXPECTED = "Unexpected error. We'll fix it soon!", -1


class APIException(exceptions.APIException):
    """
    Exception class that caught by renderer and produce pretty output.

    It also has ``error_code`` attribute that may be set by other app otherwise it'll be ``-1``
    """

    def __init__(self, detail=None, code=None, param=None):
        if isinstance(param, dict):
            detail = detail.format(**param)

        super().__init__(detail=detail, code=code)


class NotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND


class ValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
