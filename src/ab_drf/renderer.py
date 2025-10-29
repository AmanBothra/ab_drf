from rest_framework import renderers, status

RESPONSE_MESSAGE = {
    status.HTTP_200_OK: 'Data',
    status.HTTP_201_CREATED: 'Created',
    status.HTTP_204_NO_CONTENT: 'No Content',
    status.HTTP_400_BAD_REQUEST: 'Bad Request',
    status.HTTP_401_UNAUTHORIZED: 'Unauthorized',
    status.HTTP_403_FORBIDDEN: 'Forbidden',
    status.HTTP_405_METHOD_NOT_ALLOWED: 'Method Not Found',
    status.HTTP_404_NOT_FOUND: 'Not Found',
    status.HTTP_500_INTERNAL_SERVER_ERROR: 'Internal Server Error',
    status.HTTP_501_NOT_IMPLEMENTED: 'Method not Implemented'
}


class CustomRenderer(renderers.JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        renderer_context = renderer_context or {}
        response = renderer_context.get('response')
        status_code = getattr(response, 'status_code', None)

        sanitized_payload = data.copy() if isinstance(data, dict) else data
        message = self._extract_message(sanitized_payload, status_code)
        content, additional_info = self._extract_content(sanitized_payload)

        if status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_204_NO_CONTENT]:
            envelope = {
                'success': True,
                'message': message,
                'status': status_code,
            }
            if additional_info is not None:
                envelope['additional_info'] = additional_info

            if content is not None:
                if isinstance(content, dict) and 'results' in content:
                    envelope.update({
                        'count': content.get('count'),
                        'next': content.get('next'),
                        'previous': content.get('previous'),
                        'results': content.get('results')
                    })
                else:
                    envelope.update({'results': content})
        else:
            envelope = {
                'success': False,
                'error': {},
                'message': message,
                'status': status_code
            }
            if isinstance(content, dict):
                if 'detail' in content:
                    envelope['error']['non_field_errors'] = [content['detail']]
                elif 'non_field_errors' in content:
                    envelope['error']['non_field_errors'] = content['non_field_errors']
                else:
                    envelope['error'] = self.flatten_field_errors(content)
            elif content is not None:
                if isinstance(content, list):
                    envelope['error']['non_field_errors'] = content
                else:
                    envelope['error']['non_field_errors'] = [content]

        return super().render(envelope, accepted_media_type, renderer_context)

    def _extract_message(self, payload, status_code):
        default_message = RESPONSE_MESSAGE.get(status_code)
        if not isinstance(payload, dict):
            return default_message

        message = payload.pop('message', None)
        response_data = payload.get('response_data')
        if message is None and isinstance(response_data, dict):
            message = response_data.get('response_message')

        return message or default_message

    def _extract_content(self, payload):
        if not isinstance(payload, dict):
            return payload, None

        response_data = payload.pop('response_data', None)
        content_source = response_data if response_data is not None else payload

        additional_info = None
        if isinstance(content_source, dict):
            additional_info = content_source.pop('additional_info', None)
            content_source.pop('response_message', None)

        if additional_info is None and isinstance(payload, dict):
            additional_info = payload.pop('additional_info', None)

        return content_source, additional_info

    def flatten_field_errors(self, data):
        field_errors = {}
        for field, errors in data.items():
            if isinstance(errors, list) and len(errors) == 1:
                field_errors[field] = errors[0]
            else:
                field_errors[field] = errors
        return field_errors
