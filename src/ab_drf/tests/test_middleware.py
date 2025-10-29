from io import BytesIO

import django
from django.conf import settings
from django.http import FileResponse, HttpResponse, StreamingHttpResponse
from django.test import RequestFactory, SimpleTestCase

if not settings.configured:
    settings.configure(
        SECRET_KEY='test',
        ALLOWED_HOSTS=['testserver'],
        USE_TZ=True,
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
        INSTALLED_APPS=['django.contrib.auth', 'django.contrib.contenttypes'],
        MIDDLEWARE=[],
        ROOT_URLCONF=__name__,
        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'APP_DIRS': True,
                'OPTIONS': {'context_processors': []},
            }
        ],
        DEFAULT_AUTO_FIELD='django.db.models.AutoField',
    )
    django.setup()

from ab_drf.middleware import HeadInfoMiddleware


class HeadInfoMiddlewareTests(SimpleTestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()

    def get_request(self):
        return self.factory.get('/')

    def test_sets_content_length_when_content_available(self):
        def get_response(_):
            return HttpResponse('hello')

        middleware = HeadInfoMiddleware(get_response)
        response = middleware(self.get_request())

        self.assertEqual(response['Content-Length'], str(len(response.content)))

    def test_preserves_existing_content_length_header(self):
        def get_response(_):
            response = HttpResponse('hello')
            response['Content-Length'] = '123'
            return response

        middleware = HeadInfoMiddleware(get_response)
        response = middleware(self.get_request())

        self.assertEqual(response['Content-Length'], '123')

    def test_streaming_response_does_not_require_content(self):
        def get_response(_):
            return StreamingHttpResponse(iter(['hello']))

        middleware = HeadInfoMiddleware(get_response)

        response = middleware(self.get_request())

        self.assertIsNone(response.get('Content-Length'))

    def test_file_response_does_not_require_content(self):
        def get_response(_):
            file_like = BytesIO(b'hello')
            return FileResponse(file_like)

        middleware = HeadInfoMiddleware(get_response)
        expected_length = get_response(None).get('Content-Length')

        response = middleware(self.get_request())

        self.assertEqual(response.get('Content-Length'), expected_length)
