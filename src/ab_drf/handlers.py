"""
========
Handlers
========
Holds logger handler classes
"""

from raven.contrib.django.raven_compat import handlers


class SentryHandler(handlers.SentryHandler):
    """
    Extends SentryHandler feature that adds thread id to record
    """

    def _emit(self, record):
        request = getattr(record, 'request', None)
        request_id = None
        if request:
            request_id = getattr(request, 'id', None)

        tags = getattr(record, 'tags', {})
        tags.update({
            'thread': record.thread,
            'request_id': request_id
        })
        record.tags = tags

        return super(SentryHandler, self)._emit(record)
