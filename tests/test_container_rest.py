# noinspection PyPackageRequirements
import json

import pytest
from django.contrib.auth.models import User, Permission
from guardian.shortcuts import assign_perm

from .app.models import Container, ItemA


@pytest.mark.django_db(transaction=True)
class TestContainerRest:

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
    def test_container_rest(self, request, client, user, read, write, guardian_read, guardian_write, action):

        if not user.is_anonymous:
            client.force_login(user)

        # guardian_read_true
        # guardian_write_true
        # read_false
        # write_true
        # action_change

        for c in Container.objects.all():
            resource_url = self.container_url(c)

            expected_read_code = 404
            if read:
                expected_read_code = 200
            if guardian_read and c in self.guardian_containers:
                expected_read_code = 200

            if action == 'view':
                resp = client.get(resource_url)
                expected_result_code = expected_read_code
            elif action == 'change':
                resp = client.patch(resource_url, json.dumps({}), content_type='application/json')
                if expected_read_code == 404:
                    expected_result_code = 404
                else:
                    if read or guardian_read and c in self.guardian_containers:
                        expected_result_code = 403
                    else:
                        expected_result_code = 404
                    if write:
                        expected_result_code = 200
                    if guardian_write and c in self.guardian_containers:
                        expected_result_code = 200
            else:
                raise NotImplementedError('Action %s is not implemented in test' % action)

            assert resp.status_code == expected_result_code, \
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

    def container_url(self, container):
        return '/container/%s/' % container.id
