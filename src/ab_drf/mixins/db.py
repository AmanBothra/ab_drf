__all__ = ['AddUpdateTimeModelMixin', 'ViewPermModelMetaMixin']

from django.db import models
from django.db.models import Model
from django.utils.translation import gettext as _


class AddUpdateTimeModelMixin(Model):
    """
    Adds created_at and updated_at fields to a model
    """
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        abstract = True


class ViewPermModelMetaMixin:
    """
    Adds view permission to a model along with other default permissions.
    """
    default_permissions = ('add', 'change', 'delete', 'view')
