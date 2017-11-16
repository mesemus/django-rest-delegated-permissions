import json

# noinspection PyPackageRequirements
import pytest
from django.contrib.auth.models import User, Permission, AnonymousUser
from guardian.shortcuts import assign_perm

from tests.app.models import Container, ItemA


@pytest.mark.django_db(transaction=True)
class TestDelegationAlongForeignKey:
    @pytest.fixture(autouse=True)
    def environ(self):
        self.container = Container.objects.create(name='container')
        self.item = ItemA.objects.create(name='ItemA', parent=self.container)

        self.view_permission = Permission.objects.get(codename='view_container')
        self.change_permission = Permission.objects.get(codename='change_container')

    #
    # Test reading
    #

    @pytest.mark.matrix(
        names=['user'],
        combs=[
            {
                'user': ['anonymous', 'allowed_read_user', 'allowed_readwrite_user',
                         'not_allowed_user', 'allowed_guardian_user', 'allowed_guardian_read_user'],
            },
        ])
    def test_access(self, client,
                    container_url, item_url,
                    user, access_test_result_code):

        if not user.is_anonymous():
            client.force_login(user)

        resp = client.get(container_url)
        assert resp.status_code == access_test_result_code

        resp = client.get(item_url)
        assert resp.status_code == access_test_result_code

    @pytest.fixture()
    def access_test_result_code(self, user):
        if user.is_anonymous() or user.username == 'not_allowed_user':
            return 404

        if user.username in ('allowed_read_user',
                             'allowed_guardian_user', 'allowed_guardian_read_user',
                             'allowed_readwrite_user'):
            return 200

    #
    # Test modification
    #

    @pytest.mark.matrix(
        names=['user'],
        combs=[
            {
                'user': ['anonymous', 'allowed_read_user', 'allowed_readwrite_user',
                         'not_allowed_user', 'allowed_guardian_user', 'allowed_guardian_read_user'],
            },
        ])
    def test_modify(self, client,
                    container_url, item_url,
                    user, modify_test_result_code):

        if not user.is_anonymous():
            client.force_login(user)

        resp = client.patch(container_url, json.dumps({}), content_type='application/json')
        assert resp.status_code == modify_test_result_code['container']

        resp = client.patch(item_url, json.dumps({}), content_type='application/json')
        assert resp.status_code == modify_test_result_code['item']

    @pytest.fixture()
    def modify_test_result_code(self, user):
        if not user or user.username == 'not_allowed_user':
            return {'container': 404, 'item': 404}
        if user.username in ('allowed_read_user', 'allowed_guardian_read_user'):
            return {'container': 405, 'item': 403}
        if user.username in ('allowed_guardian_user', 'allowed_readwrite_user'):
            return {'container': 405, 'item': 200}

    #
    # Users
    #

    @pytest.fixture()
    def user_allowed_read_user(self):
        user = User.objects.create(username='allowed_read_user')
        user.user_permissions.add(self.view_permission)
        return user

    @pytest.fixture()
    def user_anonymous(self):
        return AnonymousUser()

    @pytest.fixture()
    def user_not_allowed_user(self):
        return User.objects.create(username='not_allowed_user')

    @pytest.fixture()
    def user_allowed_guardian_user(self):
        user = User.objects.create(username='allowed_guardian_user')
        assign_perm(self.view_permission, user, self.container)
        assign_perm(self.change_permission, user, self.container)
        return user

    @pytest.fixture()
    def user_allowed_guardian_read_user(self):
        user = User.objects.create(username='allowed_guardian_read_user')
        assign_perm(self.view_permission, user, self.container)
        return user

    @pytest.fixture()
    def user_allowed_readwrite_user(self):
        user = User.objects.create(username='allowed_readwrite_user')
        user.user_permissions.add(self.view_permission)
        user.user_permissions.add(self.change_permission)
        return user

    #
    # Resources
    #
    @pytest.fixture()
    def container_url(self):
        return '/container/%s/' % self.container.id

    @pytest.fixture()
    def item_url(self):
        return '/item/A/%s/' % self.item
