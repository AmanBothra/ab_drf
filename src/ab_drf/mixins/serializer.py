__all__ = ['DynamicFieldsSerializerMixin', 'ExcludeOnUpdateSerializerMixin',
           'InjectReqUserSerializerMixin']

from django.http import QueryDict


class DynamicFieldsSerializerMixin:
    """
    Returns only attributes passed in `query_params['fields']`

    Eg:
        /myendpoint?fields=name,email,id
    """

    @property
    def _readable_fields(self):
        all_fields = super()._readable_fields
        query_fields = self.query_fields

        for field in all_fields:
            field_name = getattr(field, 'name', None) or getattr(field, 'field_name', None)

            if not query_fields:
                yield field
            elif query_fields and field_name in query_fields:
                yield field

    @property
    def query_fields(self):
        try:
            fields = self.context['request'].query_params['fields']
        except (KeyError, AttributeError):
            return

        return fields.split(',')


class ExcludeOnUpdateSerializerMixin:
    """
    Excludes defined fields in `Meta.exclude_on_update` when making update request
    """

    def update(self, instance, validated_data):
        # Exclude those fields defined under Meta.exclude_on_update attribute
        exclude_on_update = getattr(self.Meta, 'exclude_on_update', [])
        for field in exclude_on_update:
            validated_data.pop(field, None)

        return super().update(instance, validated_data)


class NewSerializerMixin:
    """
    A serializer mixin to create a serializer with new meta attributes.

    Eg:
    ```
    class MySerializer(NewSerializerMixin, Serializer):
        class Meta:
            fields = '__all__'

    # When it's required that we need existing serializer with different fields
    MyRefSerializer = MySerializer.New(fields=('abc', 'xyz'))
    ```
    """

    @classmethod
    def New(cls, **meta_kwargs):
        class NewCls(cls):
            class Meta(cls.Meta):
                pass

        for k, v in meta_kwargs.items():
            setattr(NewCls.Meta, k, v)

        return NewCls


class InjectReqUserSerializerMixin:
    """
    Automatically sets a model's field to request.user

    Usage:

    class MySerializer(AutoSetSerializerMixin, ModelSerializer):
        class Meta:
            ...
            model_user_field = 'user'
    """

    def to_internal_value(self, data):
        model_user_field = getattr(self.Meta, 'model_user_field')
        if model_user_field:
            if isinstance(data, QueryDict):
                data._mutable = True
            data[model_user_field] = getattr(self.context['request'].user, 'id')
            if isinstance(data, QueryDict):
                data._mutable = False
        return super().to_internal_value(data)
