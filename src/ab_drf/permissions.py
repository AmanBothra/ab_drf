import logging
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.permissions import BasePermission

L = logging.getLogger(__name__)


class DjangoModelPermissionsWithRead(DjangoModelPermissions):

    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": [],
        "HEAD": [],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }


class IsOwnerPermissions(BasePermission):
    """
    Permission class that grant permission according to object owner.

    :param bool ownership_fields: List of attribute of model property that specify the ownership \
    of object, If it's an empty object, ``True`` will always return.

    .. note:: Condition check on ``ownership_fields`` will be done in ORing fashion
    """

    def has_object_permission(self, request, view, obj):
        """
        Checks for the single object if its user is same as obj. If you want to skip the owner
        permission for LISTing the data, you can set `skip_owner_filter=True` in viewset class
        """
        ownership_fields = getattr(view, "ownership_fields", None)

        # If it's explicitly mentioned to empty
        if not ownership_fields or request.method == "GET":
            return True

        _u = request.user

        # Requesting user is accessing to himself?
        if _u == obj:
            return True

        result = any(
            _u == self._get(obj, field) or _u.id == self._get(obj, field)
            for field in ownership_fields
        )
        if result is False:
            logging.warning(
                "Permission denied",
                extra={"user": _u, "ownership_fields": ownership_fields, "object": obj},
            )

        return result

    @staticmethod
    def _get(obj, path):
        paths = path.split("__")

        for p in paths:
            obj = getattr(obj, p, None)
            if obj is None:
                return

        return obj


class ActionPermissions(BasePermission):
    """
    Permission class that checks for custom permissions defined under model's meta option.

    Model permission name should match with the custom action defined in viewset class.
    for eg, if ``action_pay()`` defined under viewset, model permission set should contain custom
    permission name `action_pay`.

    ``has_permission()`` will match for ``<app_label>.<action_name>`` as permission name if user
    has.

    .. note:: Be careful using this class as it doesn't check anything apart from custom \
    permissions.
    """

    def has_permission(self, request, view):
        model_cls = getattr(view, "model", None)
        queryset = getattr(view, "queryset", None)

        if model_cls is None and queryset is not None:
            model_cls = queryset.model

        expected_perm = "%(app_label)s.%(action_name)s" % {
            "app_label": model_cls._meta.app_label,
            "action_name": view.action,
        }

        return request.user.has_perm(expected_perm)


class AllowGetOnly(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        return request.user and request.user.is_authenticated


class IsAdmin(BasePermission):
    """
    Allows access only to super users.
    """

    def has_permission(self, request, view):
        if request.user != None and request.user.is_anonymous == False:
            if request.user != None and request.user.permissions.is_admin:
                return True
        return False
