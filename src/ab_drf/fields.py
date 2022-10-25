# -*- coding: utf-8 -*-
import six
import uuid
import base64
from django.utils import timezone
from django.core.files.base import ContentFile
from rest_framework import serializers

# -----------------------------------------------------------------------------


class DateTimeTzAwareField(serializers.DateTimeField):
    """Ensure UTC time is in our local timezone."""

    def to_representation(self, value):
        value = timezone.localtime(value)
        return super().to_representation(value)

class Base64FileField(serializers.FileField):
    def to_internal_value(self, data):
        if isinstance(data, six.string_types):
            if "data:" in data and ";base64," in data:
                header, data = data.split(";base64,")

            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail("invalid_file")

            file_name = str(uuid.uuid4())[:12]  # 12 characters are more than enough.
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = "%s.%s" % (
                file_name,
                file_extension,
            )
            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64FileField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension
        return extension