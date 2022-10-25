"""
===========
Middleware
===========
"""
import os
import socket
import uuid

from django.utils import timezone

branch = os.environ.get('APP_BRANCH') or 'n/a'
commit_hash = os.environ.get('APP_COMMIT_HASH') or 'n/a'


class HeadInfoMiddleware(object):
    """
    Adds these extra headers to response

    * ``X-Runtime``: Time to produce the output
    * ``X-Request-Id``: UUID to identify the request
    * ``X-Version``: Git commit hash and branch name
    * ``X-Served-By``: Host name of the machine
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        start_time = timezone.now()
        request.id = uuid.uuid4().hex

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        response['X-Runtime'] = (timezone.now() - start_time).total_seconds()
        response['X-Request-Id'] = request.id
        response['X-Version'] = '%s#%s' % (branch, commit_hash)
        response['X-Served-By'] = socket.gethostname()
        response['Content-Length'] = len(response.content)

        return response
