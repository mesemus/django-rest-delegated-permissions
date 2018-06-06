from rest_delegated_permissions.permissions import BasePermission


class OwnerPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

    def filter(self, rest_permissions, filtered_queryset, user, action):
        """
        Must be a generator returning filters to be ORed later

        :param rest_permissions:    current RestPermissions instance
        :param filtered_queryset:   queryset to be filtered
        :param user:                current user
        :param action:              REST action being performed (such as view, change, delete)
        :return:
        """
        yield filtered_queryset.filter(owner=user)

    def has_permission(self, request, view):
        # filter will limit it
        return True

