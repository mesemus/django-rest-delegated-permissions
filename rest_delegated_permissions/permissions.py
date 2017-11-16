import inspect
import operator

from django.contrib.contenttypes.models import ContentType
from django.db.models import Exists, OuterRef, Value, ExpressionWrapper, BooleanField
from guardian.shortcuts import get_objects_for_user
from rest_condition import Condition
from rest_framework import permissions
import logging

from rest_framework.permissions import DjangoModelPermissions

log = logging.getLogger(__file__)


def get_delegated_objects(obj, field_names):
    for perm_field_name in field_names:
        perm_field = obj._meta.get_field(perm_field_name)
        delegated_objects = []
        if perm_field.one_to_many or perm_field.many_to_many:
            delegated_objects = getattr(obj, perm_field_name).all()
        elif hasattr(obj, '%s_id' % perm_field_name) and getattr(obj, '%s_id' % perm_field_name):
            delegated_objects = [getattr(obj, perm_field_name)]
        for delegated_obj in delegated_objects:
            yield delegated_obj


class OwnerPermission():
    def __init__(self, owner_username_path):
        self.owner_username_path = owner_username_path

    def has_object_permission(self, request, view, obj):
        return type(obj).objects.filter(**{self.owner_username_path: request.user.username}, pk=obj.pk).exists()

    def get_queryset_filters(self, rest_permissions, qs, user, action):
        yield qs.filter(**{self.owner_username_path: user.username}) \
            .annotate(__ex=ExpressionWrapper(Value(True), output_field=BooleanField()))


class DelegatedView:
    def __init__(self, rest_permissions, model_class, request, action):
        self.request = request
        self.action = action
        self.rest_permissions = rest_permissions
        self.model_class = model_class

    def get_queryset(self):
        return self.rest_permissions.create_queryset_factory(self.model_class)(self.request.user, self.action)


class DelegatedPermission(permissions.BasePermission):

    def __init__(self, rest_permissions, *delegated_fields):
        self.rest_permissions = rest_permissions
        self.delegated_fields = delegated_fields

    def has_object_permission(self, request, view, obj):
        for delegated_obj in get_delegated_objects(obj, self.delegated_fields):
            if not delegated_obj:
                continue
            delegated_permissions = self.rest_permissions.permissions_for_model(delegated_obj)
            delegated_view = DelegatedView(self.rest_permissions, type(delegated_obj), request, view.action)

            if delegated_permissions.has_object_permission(request, delegated_view, delegated_obj):
                return True

        return False

    def get_queryset_filters(self, rest_permissions, qs, user, action):
        for delegated_field_name in self.delegated_fields:
            fld = qs.model._meta.get_field(delegated_field_name)
            related_model = fld.related_model
            related_model_qs = rest_permissions.create_queryset_factory(related_model)(user, action)

            yield qs.annotate(__ex=Exists(related_model_qs.filter(pk=OuterRef(delegated_field_name)))) \
                .filter(__ex=True)


class DjangoCombinedPermission:
    def __init__(self):
        self.model_permissions  = permissions.DjangoModelPermissions()
        self.object_permissions = permissions.DjangoObjectPermissions()

    def has_object_permission(self, request, view, obj):
        return self.model_permissions.has_permission(request, view) or \
               self.object_permissions.has_object_permission(request, view, obj)

    def get_queryset_filters(self, rest_permissions, qs, user, action):
        operation = {
            'retrieve': 'view',
            'view': 'view',
            'update': 'change',
            'change': 'change',
            'delete': 'delete',
            'partial_update': 'change'
        }[action]
        ct = ContentType.objects.get_for_model(qs.model)
        perm = '%s.%s_%s' % (ct.app_label, operation, ct.model)
        if user.has_perm(perm):
            yield qs.annotate(__ex=ExpressionWrapper(Value(True), output_field=BooleanField()))
        else:
            # add queryset for guardian
            guardian_qs = get_objects_for_user(user, [perm], qs) \
                .annotate(__ex=ExpressionWrapper(Value(True), output_field=BooleanField()))
            yield guardian_qs




class RestPermissions:
    def __init__(self, default_queryset_factory=lambda model: model.objects.all(), add_django_permissions=True):
        self.default_queryset_factory = default_queryset_factory
        self.add_django_permissions = add_django_permissions
        self.model_permission_map = {}

    def update_permissions(self, model_permission_map):
        for model_class, model_permissions in model_permission_map.items():
            if not isinstance(model_permissions, list) and not isinstance(model_permissions, tuple):
                model_permissions = [model_permissions]
            self.set_model_permissions(model_class, model_permissions)

    def set_model_permissions(self, model_class, model_permissions):
        if self.add_django_permissions:
            perms = list(model_permissions)
            perms.insert(0, DjangoCombinedPermission())
        else:
            perms = model_permissions
        self.model_permission_map[model_class] = Condition.Or(*perms)

    def filtered_model_queryset(self, model_class, root_queryset, user, action):
        perms = self.model_permission_map[model_class].perms_or_conds
        for perm in perms:
            yield from self._permission_to_queryset(perm, root_queryset, user, action)

    def _permission_to_queryset(self, perm, root_queryset, user, action):
        """
        Converts permission into a generator of querysets. Ignores DjangoModelPermissions and DjangoObjectPermissions,
        because they are handled by guardian in the caller function (model_filter)

        :param perm:            the permission being converted
        :param root_queryset:   queryset for the model being checked
        :param user:            user for which the check is made
        :param action:       action being performed (such as view, change, ...)
        :return:                a generator of querysets
        """
        if isinstance(perm, Condition):
            if perm.negated:
                log.error('Negated subcondition is not implemented in .queryset(), expect narrower results')
            elif perm.reduce_op == operator.or_:
                for subperm in perm.perms_or_conds:
                    yield from self._permission_to_queryset(subperm, root_queryset, user, action)
            elif perm.reduce_op == operator.and_:
                # return intersection of unions
                intersection_querysets = []
                for subperm in perm.perms_or_conds:
                    subperm_querysets = list(self._permission_to_queryset(subperm, root_queryset, user, action))
                    if subperm_querysets:
                        intersection_querysets.append(subperm_querysets[0].union(*subperm_querysets[1:]))
                if intersection_querysets:
                    yield intersection_querysets[0].intersection(*intersection_querysets[1:])
            else:
                log.error('Subconditions are not implemented in .queryset(), expect narrower results')
        else:
            # django model permissions and object permissions are handled in model_filter() function
            # (faster for cases where user is assigned rights directly)
            yield perm.get_queryset_filters(self, root_queryset, user, action)

    def permissions_for_model(self, model_class_or_model):
        print("permissions for model called")
        if inspect.isclass(model_class_or_model):
            model_class = model_class_or_model
        else:
            model_class = type(model_class_or_model)
        return self.model_permission_map[model_class]

    def apply(self):
        """
        Sets premissions for a ViewSet class
        """

        def decorate(viewset_class):
            model_class = getattr(viewset_class, 'model', getattr(viewset_class, 'queryset').model)

            condition = self.model_permission_map[model_class]

            class Permission(permissions.BasePermission):
                def has_object_permission(self, request, view, obj):
                    return condition.has_object_permission(request, view, obj)

                def has_permission(self, request, view):
                    # everyone is allowed as the query set is filtered (for read) and
                    # has_object_permission is applied for update/delete
                    # create must be handled separately
                    return True

            viewset_class.permission_classes = (Permission,)

            model_queryset_factory = self.create_queryset_factory(model_class)

            # set up queryset
            def get_queryset(view_set):
                # get queryset just for viewing
                return model_queryset_factory(view_set.request.user, 'view')

            viewset_class.get_queryset = get_queryset

            return viewset_class

        return decorate

    def create_queryset_factory(self, model_class):
        """
        returns lambda (user, action) => queryset(model_class)
        """

        def model_filter(user, action):
            querysets = []
            qs = self.get_base_queryset(model_class)

            for partial_qs in self.filtered_model_queryset(model_class, qs, user, action):
                querysets.extend(partial_qs)

            return querysets[0].union(*querysets[1:])

        return model_filter

    def get_base_queryset(self, model_class):
        return self.default_queryset_factory(model_class)
