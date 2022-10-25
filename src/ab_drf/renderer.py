"""
========
Renderer
========
Change the framework's standard response structure to specific response.

The response design is follow

For single object or data::


    {
        "data": {
        }
    }

For list of object::

    {
        "meta": {
            "count": "TOTAL RECORD COUNT"
            "next": "NEXT PAGE LINK"
            "previous": "PREVIOUS PAGE LINK"
        },
        "data": [
        ]
    }

When error occurs::

    {
        "error": {
            "type": "ERROR TYPE",
            "detail": "HUMAN READABLE MESSAGE",
            "status_code": "APPROPRIATE STATUS CODE",
            "error_code": "ERROR CODE"
            "field_errors": {FIELD_NAME: [...error]},
            "non_field_errors": []
        }
    }
"""
from rest_framework.renderers import JSONRenderer as RFJSONRenderer

class JSONRenderer(RFJSONRenderer):
    """
    Override the ``render()`` of the rest framework JSONRenderer to produce JSON output as per \
    API specification
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):

        response_data = {}
        context = 'data'  # Default

        # When exception handler will pass the response, we would expect
        # the context to be `error`
        if isinstance(data, dict) and data.get('_context') == 'error':
            context = 'error'
            data.pop('_context', None)

            field_errors = self._pop_field_errors(data)
            data['field_errors'] = field_errors

            # Normalizing detail field in error, only first element of dict should be visible
            data['detail'] = self._get_detail(data)
            # Always return the key
            data['non_field_errors'] = data.pop('non_field_errors', [])

        # check if the results have been paginated
        if isinstance(data, dict) and 'results' in data:
            # add the resource key and copy the results
            response_data[context] = data.pop('results')
            response_data['meta'] = data
        else:
            response_data[context] = data

        # call super to render the response
        response = super().render(response_data, accepted_media_type, renderer_context)

        return response

    def _get_detail(self, d):
        data = d.copy()

        if data.get('non_field_errors'):
            detail = data.pop('non_field_errors')[0]
        elif data.get('detail'):
            detail = data['detail']
        else:
            detail = 'Invalid request data.'

        return detail

    def _pop_field_errors(self, data):
        keys = list(data.keys())

        return {k: data.pop(k) for k in keys if k not in
                ['type', 'error_code', 'status_code', 'non_field_errors', 'detail']}
