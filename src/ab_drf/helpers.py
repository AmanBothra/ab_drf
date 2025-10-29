"""
=======
Helpers
=======
Useful helper methods that frequently used in this project
"""

__all__ = ['custom_exception_handler']

import inspect
import logging
import mimetypes
import os
import re
import traceback
import json

import sys
from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import exception_handler
from django.contrib.admin.utils import NestedObjects
from django.utils.html import format_html
from django.utils.text import capfirst
from django.urls import reverse
from django.utils.encoding import force_str
from django.urls.exceptions import NoReverseMatch

from src.ab_drf.errors import ErrorMessage

from . import errors as err

L = logging.getLogger('app.' + __name__)

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def custom_exception_handler(exc, context):
    """
    Replace rest_framework's default handler to generate error response as per API specification
    """

    #: Call REST framework's default exception handler first,
    #: to get the standard error response.
    response = exception_handler(exc, context)
    request = context.get('request')

    # Getting originating location of exception
    frm = inspect.trace()[-1]
    mod = inspect.getmodule(frm[0])
    func = traceback.extract_tb(sys.exc_info()[2])[-1][2]
    log_extra = {'request': request, 'request_id': request.id,
                 'culprit': "%s in %s" % (mod.__name__, func)}

    if response is None and settings.DEBUG:
        return response

    if response:
        L.warning(exc, extra=log_extra, exc_info=True)
    else:
        L.exception(exc, extra=log_extra)

    # Response is none, meaning builtin error handler failed to generate response and it needs to
    #  be converted to json response
    if response is None:
        return custom_exception_handler(err.APIException(*ErrorMessage.UNEXPECTED), context)

    # Passing context to help the renderer to identify if response is error or normal data
    if isinstance(response.data, list):
        response.data = response.data[0]

    response.data['_context'] = 'error'
    response.data['type'] = exc.__class__.__name__
    response.data['status_code'] = response.status_code
    response.data['error_code'] = getattr(exc, 'error_code', 0)

    return response


def attachment_response(file, request, remove_file=True):
    filename = os.path.basename(file)
    with open(file, 'rb') as fp:
        response = HttpResponse(fp.read())

    type_, encoding = mimetypes.guess_type(file)
    if type_ is None:
        type_ = 'application/octet-stream'

    response['Content-Type'] = type_
    response['Content-Length'] = str(os.stat(file).st_size)
    if encoding is not None:
        response['Content-Encoding'] = encoding

    # To inspect details for the below code, see http://greenbytes.de/tech/tc2231/
    if u'WebKit' in request.META['HTTP_USER_AGENT']:
        # Safari 3.0 and Chrome 2.0 accepts UTF-8 encoded string directly.
        filename_header = 'filename=%s' % filename
    elif u'MSIE' in request.META['HTTP_USER_AGENT']:
        # IE does not support internationalized filename at all.
        # It can only recognize internationalized URL, so we do the trick via routing rules.
        filename_header = ''
    else:
        # For others like Firefox, we follow RFC2231 (encoding extension in HTTP headers).
        filename_header = 'filename*=UTF-8\'\'%s' % filename

    response['Content-Disposition'] = 'attachment; ' + filename_header
    if remove_file:
        os.unlink(file)

    return response


def update_order(order_data, model):
    """Parse json data and update model order.
    Object keys should be: id, order"""
    jsondata = json.loads(order_data)
    for s in jsondata:
        # This may occur if we have an empty placeholder, it's ok
        if "id" not in s or s["id"] == "None":
            continue
        try:
            instance = model.objects.get(pk=s["id"])
            if instance.the_order != s["order"]:
                instance.the_order = s["order"]
                instance.save()
        except model.DoesNotExist:
            # Object may have been deleted, so just keep going
            continue

def get_deleted_objects(objs):
    """Based on `django/contrib/admin/utils.py`"""
    collector = NestedObjects(using="default")
    collector.collect(objs)

    def format_callback(obj):
        opts = obj._meta
        # Display a link to the admin page.
        try:
            return format_html(
                '{}: <a href="{}">{}</a>',
                capfirst(opts.verbose_name),
                # TODO: Is this going to be stable if we use something other than PK, no
                reverse(admin_urlname(opts, "update"), kwargs={"pk": obj.pk}),
                obj,
            )
        except NoReverseMatch:
            pass

        no_edit_link = "%s: %s" % (capfirst(opts.verbose_name), force_str(obj))
        return no_edit_link

    to_delete = collector.nested(format_callback)
    protected = [format_callback(obj) for obj in collector.protected]
    model_count = {
        model._meta.verbose_name_plural: len(objs)
        for model, objs in collector.model_objs.items()
    }

    return to_delete, model_count, protected

def admin_urlname(value, arg, user=None):
    """Given model opts (model._meta) and a url name, return a named pattern.
    URLs should be named as: customadmin:app_label:model_name-list"""

    pattern = "customadmin:%s:%s-%s" % (value.app_label, value.model_name, arg)
    return pattern