"""Application specific error helpers.

This module exposes a light wrapper around DRF's :class:`~rest_framework.exceptions.APIException`
that records an ``error_code`` attribute alongside the HTTP status code.  It also defines
centralised error message tuples that can be unpacked directly into :class:`APIException`.
"""

from __future__ import annotations

from typing import Any, Optional, Tuple

from rest_framework import status
from rest_framework.exceptions import APIException as DRFAPIException


class ErrorMessage:
    """Collection of standard error message tuples.

    Each tuple is ordered as ``(detail, error_code, status_code)`` so it can be unpacked
    directly when instantiating :class:`APIException`.
    """

    UNEXPECTED: Tuple[str, int, int] = (
        "An unexpected error occurred.",
        0,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


class APIException(DRFAPIException):
    """Attach ``error_code`` metadata to DRF's :class:`APIException`."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self,
        detail: Any = None,
        error_code: Optional[int] = None,
        status_code: Optional[int] = None,
        *,
        code: Any = None,
    ) -> None:
        if status_code is not None:
            self.status_code = status_code
        self.error_code = error_code or 0
        super().__init__(detail=detail, code=code)


__all__ = ("APIException", "ErrorMessage")
