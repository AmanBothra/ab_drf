import sys
import types
from unittest import mock

from django.test import SimpleTestCase
from django.urls import NoReverseMatch


errors_module = types.ModuleType("src.ab_drf.errors")


class _DummyErrorMessage:
    UNEXPECTED = ("unexpected", "Unexpected error")


class _DummyAPIException(Exception):
    pass


errors_module.ErrorMessage = _DummyErrorMessage
errors_module.APIException = _DummyAPIException
sys.modules.setdefault("src.ab_drf.errors", errors_module)

from src.ab_drf.helpers import get_deleted_objects


class DummyMeta:
    verbose_name = "dummy"
    verbose_name_plural = "dummies"
    app_label = "dummy_app"
    model_name = "dummy"


class DummyModel:
    _meta = DummyMeta()

    def __init__(self, pk):
        self.pk = pk

    def __str__(self):
        return "Grün"


class GetDeletedObjectsTests(SimpleTestCase):
    @mock.patch("src.ab_drf.helpers.reverse")
    @mock.patch("src.ab_drf.helpers.NestedObjects")
    def test_formats_deleted_and_protected_objects(self, nested_objects_mock, reverse_mock):
        dummy = DummyModel(pk=1)
        collector = mock.Mock()
        nested_objects_mock.return_value = collector

        def nested_side_effect(callback):
            return [callback(dummy)]

        collector.collect.return_value = None
        collector.nested.side_effect = nested_side_effect
        collector.protected = [dummy]
        collector.model_objs = {DummyModel: [dummy]}

        reverse_mock.side_effect = NoReverseMatch("missing")

        to_delete, model_count, protected = get_deleted_objects([dummy])

        expected_label = "Dummy: Grün"
        self.assertEqual(to_delete, [expected_label])
        self.assertEqual(protected, [expected_label])
        self.assertEqual(model_count, {DummyMeta.verbose_name_plural: 1})
        collector.collect.assert_called_once_with([dummy])
        nested_objects_mock.assert_called_once_with(using="default")
