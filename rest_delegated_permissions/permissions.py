import functools
import inspect
import logging
import operator

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Exists, OuterRef, Value, ExpressionWrapper, BooleanField
from django.db.models.query import EmptyQuerySet
from guardian.shortcuts import get_objects_for_user
from rest_condition import Condition
from rest_framework import permissions

log = logging.getLogger(__file__)


class DelegatedPermission(permissions.BasePermission):

    class DelegatedView:
        def __init__(self, rest_permissions, model_class, request, action):
            self.request = request
            self.action = action
            self.rest_permissions = rest_permissions
            self.model_class = model_class

        def get_queryset(self):
            return self.rest_permissions.create_queryset_factory(self.model_class)(self.request.user, self.action)

    def __init__(self, rest_permissions, *delegated_fields):
        self.rest_permissions = rest_permissions
        self.delegated_fields = delegated_fields

    def has_object_permission(self, request, view, obj):
        for delegated_obj in DelegatedPermission.get_delegated_objects(obj, self.delegated_fields):
            if not delegated_obj:
                continue
            delegated_permissions = self.rest_permissions.permissions_for_model(delegated_obj)
            delegated_view = DelegatedPermission.DelegatedView(self.rest_permissions, type(delegated_obj), request, view.action)

            if delegated_permissions.has_object_permission(request, delegated_view, delegated_obj):
                return True

        return False

    @staticmethod
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

    def get_queryset_filters(self, rest_permissions, qs, user, action):
        for delegated_field_name in self.delegated_fields:
            fld = qs.model._meta.get_field(delegated_field_name)
            related_model = fld.related_model
            related_model_qs = rest_permissions.create_queryset_factory(related_model)(user, action)

            filtered_qs = \
                qs.annotate(__ex=Exists(related_model_qs.filter(pk=OuterRef(delegated_field_name)))).filter(__ex=True)
            yield filtered_qs


class RestrictedViewDjangoModelPermissions(permissions.DjangoModelPermissions):
    perms_map = {}
    perms_map.update(permissions.DjangoModelPermissions.perms_map)
    perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
    perms_map['OPTIONS'] = ['%(app_label)s.view_%(model_name)s']
    perms_map['HEAD'] = ['%(app_label)s.view_%(model_name)s']


class RestrictedViewDjangoObjectPermissions(permissions.DjangoObjectPermissions):
    perms_map = {}
    perms_map.update(permissions.DjangoModelPermissions.perms_map)
    perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
    perms_map['OPTIONS'] = ['%(app_label)s.view_%(model_name)s']
    perms_map['HEAD'] = ['%(app_label)s.view_%(model_name)s']

    def has_object_permission(self, request, view, obj):
        queryset = self._queryset(view)
        model_cls = queryset.model
        user = request.user
        perms = self.get_required_object_permissions(request.method, model_cls)
        return user.has_perms(perms, obj)


class DjangoCombinedPermission:
    def __init__(self):
        self.model_permissions  = RestrictedViewDjangoModelPermissions()
        self.object_permissions = RestrictedViewDjangoObjectPermissions()

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
        perm = '%s_%s' % (operation, ct.model)

        if DjangoCombinedPermission.check_permission_exists(ct, perm):
            if user.has_perm(perm):
                yield qs.annotate(__ex=ExpressionWrapper(Value(True), output_field=BooleanField()))
            else:
                # add queryset for guardian
                guardian_qs = get_objects_for_user(user, [perm], qs) \
                    .annotate(__ex=ExpressionWrapper(Value(True), output_field=BooleanField()))
                yield guardian_qs

    @staticmethod
    def check_permission_exists(ct, perm_name):
        return Permission.objects.filter(content_type=ct, codename=perm_name).exists()


class RestPermissions:
    def __init__(self, default_queryset_factory=lambda model: model.objects.all(), add_django_permissions=True):
        self.default_queryset_factory = default_queryset_factory
        self.add_django_permissions = add_django_permissions
        self.model_permission_map = {}

    def update_permissions(self, model_permission_map):
        for model_class, model_permissions in model_permission_map.items():
            self.set_model_permissions(model_class, model_permissions)

    def set_model_permissions(self, model_class, model_permissions, overwrite=False, force_add_django_permissions=None):
        if model_class in self.model_permission_map and not overwrite:
            raise AttributeError('Permissions for %s already registered' % model_class)

        if not isinstance(model_permissions, list) and not isinstance(model_permissions, tuple):
            model_permissions = [model_permissions]

        if self.add_django_permissions and force_add_django_permissions is None or force_add_django_permissions:
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
                    subperm_querysets = [
                        x for x in self._permission_to_queryset(subperm, root_queryset, user, action)
                        if not isinstance(x, EmptyQuerySet)
                    ]
                    if subperm_querysets:
                        intersection_querysets.append(functools.reduce(operator.or_, subperm_querysets))
                    else:
                        # no queryset returned => the result is False
                        intersection_querysets = None
                        break
                if intersection_querysets:
                    yield functools.reduce(operator.and_, intersection_querysets)
            else:
                log.error('Subconditions are not implemented in .queryset(), expect narrower results')
        else:
            # django model permissions and object permissions are handled in model_filter() function
            # (faster for cases where user is assigned rights directly)
            yield perm.get_queryset_filters(self, root_queryset, user, action)

    def permissions_for_model(self, model_class_or_model):
        if inspect.isclass(model_class_or_model):
            model_class = model_class_or_model
        else:
            model_class = type(model_class_or_model)
        return self.model_permission_map[model_class]

    def apply(self, permissions=None, add_django_permissions=None):
        """
        Sets premissions for a ViewSet class
        :param permissions: If the permissions are set, they are registered upon class decoration
        :param add_django_permissions: if None, use the default, otherwise overwrite the default.
                                       Makes sense only if permissions parameter is filled as well
        """

        def decorate(viewset_class):
            model_class = getattr(viewset_class, 'model', None)
            if not model_class:
                model_class = getattr(viewset_class, 'queryset').model

            if permissions is not None:
                self.set_model_permissions(model_class, permissions,
                                           force_add_django_permissions=add_django_permissions)

            model_queryset_factory = self.create_queryset_factory(model_class)

            return type('%s_perms' % viewset_class.__name__, (viewset_class, ), {
                'permission_classes': (self.get_model_permissions(model_class),),
                'get_queryset': lambda view_set: model_queryset_factory(view_set.request.user, 'view')
            })

        return decorate

    def get_model_permissions(self, model_class):
        condition = self.model_permission_map[model_class]

        class _Permission(permissions.BasePermission):
            def has_object_permission(self, request, view, obj):
                return condition.has_object_permission(request, view, obj)

            def has_permission(self, request, view):
                # everyone is allowed as the query set is filtered (for read) and
                # has_object_permission is applied for update/delete
                # create must be handled separately
                return True

        return _Permission

    def create_queryset_factory(self, model_class):
        """
        returns lambda (user, action) => queryset(model_class)
        """

        def model_filter(user, action):
            querysets = []
            qs = self.get_base_queryset(model_class)

            for partial_qs in self.filtered_model_queryset(model_class, qs, user, action):
                querysets.extend(partial_qs)
            querysets = [
                x for x in querysets if not isinstance(x, EmptyQuerySet)
            ]
            if querysets:
                return functools.reduce(operator.or_, querysets).distinct()
            return model_class.objects.none()

        return model_filter

    def get_base_queryset(self, model_class):
        return self.default_queryset_factory(model_class)
