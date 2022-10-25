from django.db import models
from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _


class MyModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True

    def to_dict(self):
        data = model_to_dict(self)
        data["created_at"] = self.created_at
        data["updated_at"] = self.updated_at
        return data
