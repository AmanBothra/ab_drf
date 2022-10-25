from celery import task
from django.contrib.contenttypes.models import ContentType


@task
def delete_objects(pk, content_type_id):
    content_type = ContentType.objects.get(id=content_type_id)
    model = content_type.model_class()
    obj = model.objects.get(pk=pk)
    obj.delete()