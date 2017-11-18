# noinspection PyPackageRequirements
from unittest.mock import Mock

import pytest
from django.contrib.auth.models import User, Permission, AnonymousUser
from django.db.models.query import EmptyQuerySet, EmptyResultSet
from guardian.shortcuts import assign_perm

from .app.models import Container, ItemA
from .app.viewsets import perms


@pytest.mark.django_db(transaction=True)
class TestContainerPermission:

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
    def test_container_permission(self, request, user, read, write, guardian_read, guardian_write, action):

        for c in Container.objects.all():

            should_be_allowed = False

            req = Mock()
            req.user = user

            if action == 'view':
                req.method = 'GET'
                if read:
                    should_be_allowed = True
                if guardian_read:
                    should_be_allowed = should_be_allowed or c in self.guardian_containers
            elif action == 'change':
                req.method = 'PATCH'
                if write:
                    should_be_allowed = True
                if guardian_write:
                    should_be_allowed = should_be_allowed or c in self.guardian_containers

            class DummyViewSet:
                pass

            viewset = DummyViewSet()
            viewset.request = req
            viewset.action = action
            viewset.model = Container
            viewset.queryset = Container.objects.all()

            perm_handler = perms.get_model_permissions(Container)()

            is_allowed = perm_handler.has_object_permission(req, viewset, c)

            assert is_allowed == should_be_allowed, \
                   "The container had id %s, the ids of guardian containers were %s" % (
                       c.id,
                       [x.id for x in self.guardian_containers]
                   )

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

    # endregion

    # region Actions

    @pytest.fixture
    def action_view(self):
        return 'view'

    @pytest.fixture
    def action_change(self):
        return 'change'

    # endregion
