# noinspection PyPackageRequirements
import pytest
from django.contrib.auth.models import User, Permission, AnonymousUser
from django.db.models.query import EmptyQuerySet, EmptyResultSet
from guardian.shortcuts import assign_perm

from .app.models import Container, ItemA
from .app.viewsets import perms


@pytest.mark.django_db(transaction=True)
class TestContainerQuerySets:

    # region Common

    # noinspection PyAttributeOutsideInit
    @pytest.fixture(autouse=True)
    def environ(self):
        self.containers = []
        self.items_A = []
        self.guardian_items_A = []

        for i in range(10):
            container = Container.objects.create(name='container_%s' % i)
            for j in range(2):
                item = ItemA.objects.create(name='ItemA_%s_%s' % (i, j), parent=container)
                self.items_A.append(item)
                if i < 5:
                    self.guardian_items_A.append(item)

            self.containers.append(container)

        self.guardian_containers = self.containers[:5]

        self.view_permission = Permission.objects.get(codename='view_container')
        self.change_permission = Permission.objects.get(codename='change_container')

    # endregion

    # region Tests

    @pytest.mark.matrix(
        names=['guardian_read', 'guardian_write', 'read', 'write', 'action'],
        combs=[
            {
                'guardian_read': ['true', 'false'],
                'guardian_write': ['true', 'false'],
                'read': ['true', 'false'],
                'write': ['true', 'false'],
                'action': [
                    'view', 'change'
                ]
            },
        ])
    def test_container_queryset(self, request, user, read, write, guardian_read, guardian_write, action):
        qs = perms.create_queryset_factory(Container)(user, action)
        print("\nOutput from %s" % request.node.name)
        try:
            print(qs.query)
        except EmptyResultSet:
            print('{empty}')
        ids = set(qs.values_list('id', flat=True))
        expected_ids = set()
        if action == 'view':
            if read:
                expected_ids.update(x.id for x in self.containers)
            if guardian_read:
                expected_ids.update(x.id for x in self.guardian_containers)
        elif action == 'change':
            if write:
                expected_ids.update(x.id for x in self.containers)
            if guardian_write:
                expected_ids.update(x.id for x in self.guardian_containers)
        assert ids == expected_ids

    # endregion

    # region Users and abstract permissions

    @pytest.fixture()
    def user(self, read, write, guardian_read, guardian_write):
        user = User.objects.create(username='a')
        if read:
            user.user_permissions.add(self.view_permission)
        if write:
            user.user_permissions.add(self.change_permission)
        if guardian_read:
            for cont in self.guardian_containers:
                assign_perm(self.view_permission, user, cont)
        if guardian_write:
            for cont in self.guardian_containers:
                assign_perm(self.change_permission, user, cont)
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