import json
import os
import sys
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(BASE_DIR, 'src'))

from django.conf import settings
import django

if not settings.configured:
    settings.configure(
        INSTALLED_APPS=['rest_framework'],
        SECRET_KEY='test-key',
        USE_TZ=True,
    )

django.setup()

from rest_framework import status
from rest_framework.response import Response

from ab_drf.renderer import CustomRenderer


class CustomRendererTests(unittest.TestCase):
    def setUp(self):
        self.renderer = CustomRenderer()

    def render(self, data, status_code):
        response = Response(data=data, status=status_code)
        rendered = self.renderer.render(
            response.data,
            renderer_context={'response': response},
        )
        return json.loads(rendered.decode('utf-8'))

    def test_success_response_with_results_and_additional_info(self):
        payload = {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [{'id': 1}],
            'additional_info': {'page': 1},
        }

        rendered = self.render(payload, status.HTTP_200_OK)

        self.assertTrue(rendered['success'])
        self.assertEqual(rendered['message'], 'Data')
        self.assertEqual(rendered['status'], status.HTTP_200_OK)
        self.assertEqual(rendered['additional_info'], {'page': 1})
        self.assertEqual(rendered['count'], 1)
        self.assertEqual(rendered['results'], [{'id': 1}])

    def test_created_response_with_response_data_message(self):
        payload = {
            'response_data': {
                'response_message': 'Created successfully',
                'results': {'id': 2},
                'additional_info': {'source': 'serializer'},
            }
        }

        rendered = self.render(payload, status.HTTP_201_CREATED)

        self.assertTrue(rendered['success'])
        self.assertEqual(rendered['message'], 'Created successfully')
        self.assertEqual(rendered['results'], {'id': 2})
        self.assertEqual(rendered['additional_info'], {'source': 'serializer'})

    def test_no_content_response_handles_none_payload(self):
        rendered = self.render(None, status.HTTP_204_NO_CONTENT)

        self.assertTrue(rendered['success'])
        self.assertEqual(rendered['message'], 'No Content')
        self.assertEqual(rendered['status'], status.HTTP_204_NO_CONTENT)
        self.assertNotIn('results', rendered)

    def test_bad_request_with_detail_message(self):
        payload = {'detail': 'Invalid input'}

        rendered = self.render(payload, status.HTTP_400_BAD_REQUEST)

        self.assertFalse(rendered['success'])
        self.assertEqual(rendered['message'], 'Bad Request')
        self.assertEqual(
            rendered['error']['non_field_errors'],
            ['Invalid input'],
        )

    def test_bad_request_with_field_errors(self):
        payload = {'username': ['This field is required.']}

        rendered = self.render(payload, status.HTTP_400_BAD_REQUEST)

        self.assertFalse(rendered['success'])
        self.assertEqual(rendered['message'], 'Bad Request')
        self.assertEqual(rendered['error']['username'], 'This field is required.')


if __name__ == '__main__':
    unittest.main()
