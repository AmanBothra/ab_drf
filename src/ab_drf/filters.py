from django.db.models import Q
from rest_framework import filters
from django_filters import Filter
from rest_framework import serializers



class OwnerOrStaffFilterBackend(filters.BaseFilterBackend):
    """
    Filters the objects based on the list of User foreign key attribute defined in
    `ownership_filter_fields`.

    It checks object's attributes against user id. All staff/admin user's are excluded from being
    filtered.

    As a matter of organization's staff/admin seeing other user's data is prevented with
    `OrganizationFilterBackend`
    """

    def filter_queryset(self, request, queryset, view):
        ownership_filter_fields = getattr(view, 'ownership_filter_fields', None)
        user = request.user

        # ignore when fields are missing
        if not ownership_filter_fields:
            return queryset

        # Allow system's staff/admin
        if user.is_superuser or user.is_staff:
            return queryset

        q = Q()
        for field in ownership_filter_fields:
            q |= Q(**{field: user.id})

        # The reason behind not directly filtering the original queryset with the filter fields
        # it gets duplicated when there's OneToMany fields are being filtered.
        # Distinct can be added but it'll become trickier with custom ordering as 'id' field
        # would always be present in ordering fields
        qs = queryset.model.objects.filter(q).values_list('id', flat=True)
        queryset = queryset.filter(id__in=qs)

        return queryset


class ListFilterField(Filter):
    """This is a custom FilterField to enable a behavior like:
    ?id=1,2,3,4 ...
    """

    def filter(self, queryset, value):

        # If no value is passed, just return the
        # initial queryset
        if not value:
            return queryset

        self.lookup_expr = "in"  # Setting the lookupexpression for all values
        list_values = value.split(",")  # Split the incoming querystring by comma

        if not all(
            [item.isdigit() for item in list_values]
        ):  # In this case, I check on isdigit()
            raise serializers.ValidationError(
                "All values in {}s are not integer.".format(str(list_values))
            )
        # If everything is fine, Just pass the execution to the Filter-class
        return super(ListFilterField, self).filter(queryset, list_values).distinct()