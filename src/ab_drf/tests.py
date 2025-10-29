import logging
import os
import sys
import types
from unittest.mock import Mock, patch

import django
from django.conf import settings

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
for path in (SRC_DIR, PROJECT_ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)


celery_module = types.ModuleType("celery")


def _identity_task(func):
    return func


celery_module.task = _identity_task
sys.modules.setdefault("celery", celery_module)

if not settings.configured:
    settings.configure(
        SECRET_KEY="test-secret-key",
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.admin",
            "rest_framework",
            "rest_framework.authtoken",
        ],
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
        MIDDLEWARE=[],
        ROOT_URLCONF=__name__,
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [],
                "APP_DIRS": True,
                "OPTIONS": {"context_processors": []},
            }
        ],
        USE_TZ=True,
        DEFAULT_AUTO_FIELD="django.db.models.AutoField",
        AUTH_PASSWORD_VALIDATORS=[],
    )
    django.setup()
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import (
    APIClient as APIClient_,
    APIRequestFactory,
    APITestCase,
)

from .viewsets import MyModelViewSet


class APIClient(APIClient_):
    def generic(self, method, path, data='',
                content_type='application/octet-stream', secure=False, **extra):

        resp = super(APIClient, self).generic(method, path, data=data, content_type=content_type,
                                              secure=secure, **extra)
        return self._fix_response(resp)

    @classmethod
    def _fix_response(cls, response):
        if response.get('Content-Type') != 'application/json':
            return response

        try:
            resp = response.json()
            response.meta = resp.get('meta')
            response.data = resp.get('data') or resp.get('error')
        except:
            pass

        return response


class TestCase(APITestCase):
    client_class = APIClient

    def __init__(self, methodName='runTest'):
        super().__init__(methodName=methodName)

    def get_client(self, user, http_authorization_prefix='Token'):
        c = APIClient()
        c.credentials(HTTP_AUTHORIZATION='%s %s' % (http_authorization_prefix, user.auth_token.key))
        return c

    def mock_timezone_now(self, time):
        try:
            from mock import patch
        except ImportError:
            raise ModuleNotFoundError

        self.patcher = patch('django.utils.timezone.now', lambda: time)
        self.addCleanup(self.patcher.stop)
        self.patcher.start()

    def setUp(self):
        super().setUp()
        settings.DEBUG = True

        self.status_code = status

        logging.disable(logging.NOTSET)


class SetupUserTestCaseMixin:
    admin_client = None
    admin_token = None
    admin = None
    user_client = None
    user_token = None
    user = None

    PWD = 'ucRLRlkwKj8o'

    def setUp(self):
        from rest_framework.authtoken.models import Token

        super().setUp()

        UserModel = get_user_model()

        self.admin = UserModel.objects.create_superuser(email='admin@stickboy.io',
                                                        password=self.PWD)
        self.user = UserModel.objects.create(email='user@stickboy.io', password=self.PWD)

        Token.objects.get_or_create(user=self.admin)
        Token.objects.get_or_create(user=self.user)

        self.admin_client = self.get_client(self.admin)
        self.user_client = self.get_client(self.user)


urlpatterns = []


class DummyInstance:
    def __init__(self, pk=1):
        self.pk = pk


class MyModelViewSetDestroyTests(TestCase):
    def setUp(self):
        super().setUp()
        self.factory = APIRequestFactory()
        self.view = MyModelViewSet.as_view({"delete": "destroy"})
        self.instance = DummyInstance()

    @patch("src.ab_drf.viewsets.delete_objects")
    @patch(
        "src.ab_drf.viewsets.get_deleted_objects", return_value=([], {"dummy": 1}, [])
    )
    def test_destroy_small_delete_uses_standard_signature(
        self, mocked_deleted, mocked_delete
    ):
        request = self.factory.delete(f"/dummy/{self.instance.pk}/")

        mocked_delete.delay = Mock()
        MyModelViewSet.destroy.__globals__["get_deleted_objects"] = mocked_deleted
        MyModelViewSet.destroy.__globals__["delete_objects"] = mocked_delete

        with patch.object(
            MyModelViewSet, "get_object", return_value=self.instance
        ) as mocked_get_object, patch.object(
            MyModelViewSet, "perform_destroy"
        ) as mocked_perform_destroy:
            response = self.view(request, pk=self.instance.pk)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mocked_get_object.assert_called_once()
        mocked_perform_destroy.assert_called_once_with(self.instance)
        mocked_deleted.assert_called_once()
        mocked_delete.delay.assert_not_called()

    @patch("src.ab_drf.viewsets.ContentType.objects.get_for_model")
    @patch("src.ab_drf.viewsets.delete_objects")
    @patch(
        "src.ab_drf.viewsets.get_deleted_objects", return_value=([], {"dummy": 150}, [])
    )
    def test_destroy_large_delete_enqueues_celery_task(
        self, mocked_deleted, mocked_delete, mocked_get_for_model
    ):
        request = self.factory.delete(f"/dummy/{self.instance.pk}/")

        mocked_delete.delay = Mock()
        mocked_get_for_model.return_value = types.SimpleNamespace(id=42)
        MyModelViewSet.destroy.__globals__["get_deleted_objects"] = mocked_deleted
        MyModelViewSet.destroy.__globals__["delete_objects"] = mocked_delete

        with patch.object(
            MyModelViewSet, "get_object", return_value=self.instance
        ), patch.object(
            MyModelViewSet, "perform_destroy"
        ) as mocked_perform_destroy:
            response = self.view(request, pk=self.instance.pk)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        mocked_deleted.assert_called_once()
        mocked_delete.delay.assert_called_once_with(self.instance.pk, 42)
        mocked_perform_destroy.assert_not_called()
