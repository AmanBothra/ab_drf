import logging
import os
import sys
import unittest


CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from django.conf import settings  # noqa: E402

if not settings.configured:  # pragma: no cover - defensive programming for test bootstrap
    settings.configure(
        DEBUG=False,
        SECRET_KEY="test-key",
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "rest_framework",
            "ab_drf",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        USE_TZ=True,
        MIDDLEWARE=[],
    )
    import django

    django.setup()

from rest_framework import status  # noqa: E402

from ab_drf.errors import APIException, ErrorMessage  # noqa: E402
from ab_drf.helpers import custom_exception_handler  # noqa: E402


class DummyRequest:
    def __init__(self, request_id: str = "dummy-request") -> None:
        self.id = request_id
        self.META = {}


class CustomExceptionHandlerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.context = {"request": DummyRequest()}
        logging.disable(logging.CRITICAL)
        self.addCleanup(logging.disable, logging.NOTSET)

    def test_wraps_unexpected_exception(self) -> None:
        try:
            raise ValueError("boom")
        except ValueError as exc:
            response = custom_exception_handler(exc, dict(self.context))

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, ErrorMessage.UNEXPECTED[2])
        self.assertEqual(response.data["detail"], ErrorMessage.UNEXPECTED[0])
        self.assertEqual(response.data["error_code"], ErrorMessage.UNEXPECTED[1])
        self.assertEqual(response.data["status_code"], ErrorMessage.UNEXPECTED[2])
        self.assertEqual(response.data["_context"], "error")
        self.assertEqual(response.data["type"], "APIException")

    def test_preserves_api_exception_metadata(self) -> None:
        try:
            raise APIException(
                "Invalid input",
                error_code=123,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except APIException as exc:
            response = custom_exception_handler(exc, dict(self.context))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Invalid input")
        self.assertEqual(response.data["error_code"], 123)
        self.assertEqual(response.data["status_code"], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["_context"], "error")
        self.assertEqual(response.data["type"], "APIException")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
