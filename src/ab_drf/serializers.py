from rest_framework import serializers


class CustomModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        exclude = kwargs.pop("exclude", None)
        read_only_fields = kwargs.pop("read_only_fields", None)

        super(CustomModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        if exclude is not None:
            existing = set(self.fields)
            for field_name in existing:
                if field_name in exclude:
                    self.fields.pop(field_name)

        if read_only_fields is not None:
            for f in read_only_fields:
                try:
                    self.fields[f].read_only = True
                except KeyError:
                    # not in fields anyway
                    pass