import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient as APIClient_, APITestCase


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
