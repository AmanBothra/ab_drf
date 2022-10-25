__all__ = ['ActionSerializerViewSetMixin', 'NestedViewSetMixin']

from collections import deque

from django.http import QueryDict
from rest_framework_extensions.mixins import NestedViewSetMixin as __NestedViewSetMixin


class ActionSerializerViewSetMixin:
    """
    a view-set mixin that returns serializer class based on action being called if specified.

    For eg.: In a view-set if following is defined

        serializer_class = MySerializer
        list_serializer_class = MyListSerializer

        serializer class `MyListSerializer` will be used when list() action
         (usually http GET for list objects.) is called.
    """

    def get_serializer_class(self):
        serializer_class = getattr(self, '%s_serializer_class' % self.action, None)

        if serializer_class:
            return serializer_class
        else:
            return super().get_serializer_class()


class NestedViewSetMixin(__NestedViewSetMixin):
    """
    Extends feature to http://chibisov.github.io/drf-extensions/docs/#nested-router-mixin

    * Method to get parent object
    * Add parent query dict to `request.data`
    """

    def create(self, request, *args, **kwargs):
        """
        Extends to inject parent object id to the request data.
        """
        self.get_parent_object()

        # Since QueryDict now immutable
        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        if type(request.data) in [list, tuple]:
            deque(map(lambda data: data.update(**self.get_parents_query_dict()), request.data))
        else:
            request.data.update(**self.get_parents_query_dict())

        request.parent_query_dict = self.get_parents_query_dict()

        return super().create(request, *args, **kwargs)

    def get_parent_object(self):
        """
        Checks the object's parent object permission and returns it
        """
        # Getting related field name
        parent_object_name = None

        # Spliting direct foreign key and nested foreign keys; later we'll have to query indirect
        # foreign key for permission
        foreign_keys = []
        for key in self.get_parents_query_dict().keys():
            if '__' in key:
                foreign_keys += key.split('__')[1:]
            else:
                parent_object_name = key

        # Getting parent model
        parent_model = self.get_queryset().model._meta.get_field(parent_object_name).related_model
        # Getting parent object
        parent_object = parent_model.objects.get(
            id=self.get_parents_query_dict().get(parent_object_name)
        )

        self.check_object_permissions(self.request, parent_object)

        __parent_object = parent_object
        for key in foreign_keys:
            __parent_object = getattr(__parent_object, key)
            self.check_object_permissions(self.request, __parent_object)

        return parent_object
