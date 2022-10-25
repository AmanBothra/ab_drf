from rest_framework import serializers
from rest_framework.fields import empty


class PassObject(object):
    pass


class BaseSerializer(serializers.ModelSerializer):
    pass_object = PassObject()

    def __init__(self, instance=None, data=empty, **kwargs):
        self.instance = instance

        if data is not empty:
            self.initial_data = data

        self.partial = kwargs.pop("partial", True)
        self.pass_object = kwargs.pop("pass_object", self.pass_object)

        kwargs.pop("many", None)

        read_only_fields = getattr(self.Meta, "read_only_fields", None)

        if read_only_fields is not None:
            if not isinstance(read_only_fields, (list, tuple)):
                raise TypeError(
                    "The `read_only_fields` option must be a list or tuple. "
                    "Got %s." % type(read_only_fields).__name__
                )

            if isinstance(read_only_fields, list):
                read_only_fields = read_only_fields + [
                    "created_at",
                    "updated_at",
                ]

            if isinstance(read_only_fields, tuple):
                read_only_fields = read_only_fields + (
                    "created_at",
                    "updated_at",
                )

            self.Meta.read_only_fields = read_only_fields

        super(BaseSerializer, self).__init__(instance, data, **kwargs)
