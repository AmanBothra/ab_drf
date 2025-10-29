# -*- coding: utf-8 -*-

from rest_framework import mixins, viewsets
from django.contrib.contenttypes.models import ContentType

from .helpers import get_deleted_objects
from .tasks import delete_objects

class MyGenericViewSet(viewsets.GenericViewSet):
    """Custom API response format."""
    
    def get_requet_method_type(self):
        return self.request.method

    def finalize_response(self, request, response, *args, **kwargs):
        # Override response (is there a better way to do this?)

        return super().finalize_response(request, response, *args, **kwargs)
    
    def destroy_object(self, request, model, pk):
        obj = model.objects.get(pk=pk)
        deleted_objects, model_count, protected = get_deleted_objects([obj])

        length_deleted_obj = 0
        for models, obj in model_count.items():
            length_deleted_obj += obj

        if length_deleted_obj > int(100):
            content_type = ContentType.objects.get_for_model(model)
            delete_objects.delay(pk, content_type.id)
            return True

        return False


class MyModelViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    MyGenericViewSet,
):
    """Custom API response format."""

    def destroy(self, request, model, pk):

        obj = model.objects.get(pk=pk)
        deleted_objects, model_count, protected = get_deleted_objects([obj])

        length_deleted_obj = 0
        for models, obj in model_count.items():
            length_deleted_obj += obj
        if length_deleted_obj > int(100):
            content_type = ContentType.objects.get_for_model(model)
            delete_objects.delay(pk, content_type.id)
            return True

        return False



class MyCreateViewSet(mixins.CreateModelMixin, MyGenericViewSet):
    """Custom API response format."""

    pass


class MyCreateListViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, MyGenericViewSet
):
    """Custom API response format."""

    pass


class MyCreateRetrieveViewSet(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, MyGenericViewSet
):
    """Custom API response format."""

    pass


class MyCreateListRetrieveViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    MyGenericViewSet,
):
    """Custom API response format."""

    pass


class MyListViewSet(mixins.ListModelMixin, MyGenericViewSet):
    """Custom API response format."""

    pass


class MyListRetrieveViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, MyGenericViewSet
):
    """Custom API response format."""

    pass


class MyRetrieveUpdateViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, MyGenericViewSet
):
    """Custom API response format."""

    pass


class MyRetrieveViewSet(mixins.RetrieveModelMixin, MyGenericViewSet):
    """Custom API response format."""

    pass


class MyUpdateViewSet(mixins.UpdateModelMixin, MyGenericViewSet):
    """Custom API response format."""

    pass


class MyRetrieveUpdateDestroyViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    MyGenericViewSet,
):
    """Custom API response format."""

    pass


class MyCreateRetrieveUpdateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    MyGenericViewSet,
):
    """Custom API response format."""

    pass


class MyCreateRetrieveUpdateViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    MyGenericViewSet,
):
    """Custom API response format."""

    pass
