# noinspection PyPackageRequirements

import pytest
from django.contrib.auth.models import User
from django.db.models.query import EmptyResultSet
from guardian.shortcuts import assign_perm

from .app.viewsets import perms


class BaseTestItemQuerySets:

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
    def test_item_queryset(self, request, user, read, write, guardian_read, guardian_write,
                            item_read, item_write, guardian_item_read, guardian_item_write,
                            action, item_class):
        qs = perms.create_queryset_factory(item_class)(user, action)
        print("\nOutput from %s" % request.node.name)
        try:
            print(qs.query)
        except EmptyResultSet:
            print('{empty}')
        ids = set(qs.values_list('id', flat=True))
        expected_ids = set()
        if action == 'view':
            if read:
                expected_ids.update(x.id for x in self.items)
            if guardian_read:
                expected_ids.update(x.id for x in self.guardian_items)
            if item_read:
                expected_ids.update(x.id for x in self.items)
            if guardian_item_read:
                expected_ids.update(x.id for x in self.guardian_directly_on_items)
        elif action == 'change':
            if write:
                expected_ids.update(x.id for x in self.items)
            if guardian_write:
                expected_ids.update(x.id for x in self.guardian_items)
            if item_write:
                expected_ids.update(x.id for x in self.items)
            if guardian_item_write:
                expected_ids.update(x.id for x in self.guardian_directly_on_items)

        assert ids == expected_ids

    # endregion

    # region Users and abstract permissions

    @pytest.fixture()
    def user(self, read, write, guardian_read, guardian_write,
             item_read, item_write, guardian_item_read, guardian_item_write):
        user = User.objects.create(username='a')
        if read:
            user.user_permissions.add(self.view_permission)
        if write:
            user.user_permissions.add(self.change_permission)
        if item_read:
            user.user_permissions.add(self.view_item_permission)
        if item_write:
            user.user_permissions.add(self.change_item_permission)
        if guardian_read:
            for cont in self.guardian_containers:
                assign_perm(self.view_permission, user, cont)
        if guardian_write:
            for cont in self.guardian_containers:
                assign_perm(self.change_permission, user, cont)
        if guardian_item_read:
            for item in self.guardian_directly_on_items:
                assign_perm(self.view_item_permission, user, item)
        if guardian_item_write:
            for item in self.guardian_directly_on_items:
                assign_perm(self.change_item_permission, user, item)
        return user

    @pytest.fixture()
    def read_true(self):
        return True

    @pytest.fixture()
    def read_false(self):
        return False

    @pytest.fixture()
    def write_true(self):
        return True

    @pytest.fixture()
    def write_false(self):
        return False

    @pytest.fixture()
    def guardian_read_true(self):
        return True

    @pytest.fixture()
    def guardian_read_false(self):
        return False

    @pytest.fixture()
    def guardian_write_true(self):
        return True

    @pytest.fixture()
    def guardian_write_false(self):
        return False

    @pytest.fixture()
    def guardian_item_read_true(self):
        return True

    @pytest.fixture()
    def guardian_item_read_false(self):
        return False

    @pytest.fixture()
    def guardian_item_write_true(self):
        return True

    @pytest.fixture()
    def guardian_item_write_false(self):
        return False

    @pytest.fixture()
    def item_read_true(self):
        return True

    @pytest.fixture()
    def item_read_false(self):
        return False

    @pytest.fixture()
    def item_write_true(self):
        return True

    @pytest.fixture()
    def item_write_false(self):
        return False
    # endregion

    # region Actions

    @pytest.fixture
    def action_view(self):
        return 'view'

    @pytest.fixture
    def action_change(self):
        return 'change'

    # endregion

    def method_teardown(self):
        pass