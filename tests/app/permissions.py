class OwnerPermission:

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

    def get_queryset_filters(self, rest_permissions, qs, user, action):
        return qs.filter(owner=user)
