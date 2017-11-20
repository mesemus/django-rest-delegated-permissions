# noinspection PyPackageRequirements
from unittest.mock import Mock

import pytest
from django.db.models.query import EmptyResultSet

from .app.viewsets import perms


class BaseTestItemPermission:
    # region Tests

    @pytest.mark.matrix(
        names=['guardian_read', 'guardian_write', 'guardian_item_read', 'guardian_item_write',
               'read', 'write', 'item_read', 'item_write', 'action'],
        combs=[
            {
                'guardian_read': ['true', 'false'],
                'guardian_write': ['true', 'false'],
                'guardian_item_read': ['true', 'false'],
                'guardian_item_write': ['true', 'false'],
                'read': ['true', 'false'],
                'write': ['true', 'false'],
                'item_read': ['true', 'false'],
                'item_write': ['true', 'false'],
                'action': [
                    'view', 'change'
                ]
            },
        ])
    def test_item_permission(self, request, user, read, write, guardian_read, guardian_write,
                             item_read, item_write, guardian_item_read, guardian_item_write,
                             action, item_class):

        self._do_test(action, guardian_item_read, guardian_item_write, guardian_read, guardian_write, item_class,
                      item_read, item_write, read, request, user, write)

    def _do_test(self, action, guardian_item_read, guardian_item_write, guardian_read, guardian_write, item_class,
                 item_read, item_write, read, request, user, write):
        for c in item_class.objects.all():

            should_be_allowed = False

            req = Mock()
            req.user = user

            # guardian_write_true
            # guardian_item_write_true
            # write_false
            # item_write_false

            if action == 'view':
                req.method = 'GET'
                if read:
                    should_be_allowed = True
                if guardian_read:
                    should_be_allowed = should_be_allowed or not not self.get_parents(c).intersection(
                        set(self.guardian_containers))
                if item_read:
                    should_be_allowed = True
                if guardian_item_read:
                    should_be_allowed = should_be_allowed or c in self.guardian_directly_on_items
            elif action == 'change':
                req.method = 'PATCH'
                if write:
                    should_be_allowed = True
                if guardian_write:
                    should_be_allowed = should_be_allowed or not not self.get_parents(c).intersection(
                        set(self.guardian_containers))
                if item_write:
                    should_be_allowed = True
                if guardian_item_write:
                    should_be_allowed = should_be_allowed or c in self.guardian_directly_on_items

            class DummyViewSet:
                pass

            viewset = DummyViewSet()
            viewset.request = req
            viewset.action = action
            viewset.model = item_class
            viewset.queryset = item_class.objects.all()

            perm_handler = self.get_perms().get_model_permissions(item_class)()

            is_allowed = perm_handler.has_object_permission(req, viewset, c)

            should_be_allowed = \
                self.transform_should_be_allowed(should_be_allowed, request, c)

            assert is_allowed == should_be_allowed, \
                "The item had id %s, parents %s, the ids of guardian containers were %s, " \
                "the ids of direct guardian items was %s" % (
                    c.id,
                    [x.id for x in self.get_parents(c)],
                    [x.id for x in self.guardian_containers],
                    [x.id for x in self.guardian_directly_on_items],
                )

    def transform_should_be_allowed(self, should_be_allowed, request, item):
        return should_be_allowed

    def get_perms(self):
        return perms

    # endregion

    def get_parents(self, x):
        try:
            return set([x.parent])
        except:
            pass

        try:
            return set(x.container.all())
        except:
            pass

        try:
            return set(x.parents.all())
        except:
            pass

        return set(x.containers.all())


class SelectiveBaseTestItemPermission(BaseTestItemPermission):
    @pytest.mark.matrix(
        names=['guardian_read', 'guardian_write', 'guardian_item_read', 'guardian_item_write',
               'read', 'write', 'item_read', 'item_write', 'action'],
        combs=[
            {
                'guardian_read': ['true', 'false'],
                'guardian_write': ['true', 'false'],
                'guardian_item_read': ['false'],
                'guardian_item_write': ['false'],
                'read': ['true', 'false'],
                'write': ['true', 'false'],
                'item_read': ['false'],
                'item_write': ['false'],
                'action': [
                    'view', 'change'
                ]
            },
        ])
    def test_item_permission(self, request, user, read, write, guardian_read, guardian_write,
                             item_read, item_write, guardian_item_read, guardian_item_write,
                             action, item_class):

        self._do_test(action, guardian_item_read, guardian_item_write, guardian_read, guardian_write, item_class,
                      item_read, item_write, read, request, user, write)
