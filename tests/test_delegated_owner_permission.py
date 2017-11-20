# noinspection PyPackageRequirements

import pytest

from tests.app.viewsets import perms2, perms3
from tests.test_item_base import BaseTestAllowOnlyOwner, BaseTestDelegatedOwner
from tests.test_item_permission_base import BaseTestItemPermission
from tests.test_users_base import BaseUsers


@pytest.mark.django_db(transaction=True)
class TestDelegatedOwnerPermission(BaseTestDelegatedOwner, BaseTestItemPermission, BaseUsers):

    def transform_should_be_allowed(self, should_be_allowed, request, item):
        has_delegated_django_permission = False
        has_delegated_owner_permission  = False
        has_item_permission             = False
        user = request.getfixturevalue('user')
        action = request.getfixturevalue('action')
        if item.parent:
            if action == 'view':
                has_delegated_django_permission = user.has_perm('view_container', item.parent) or user.has_perm('app.view_container')
            elif action == 'change':
                has_delegated_django_permission = user.has_perm('change_container', item.parent) or user.has_perm('app.change_container')
            has_delegated_owner_permission = user == item.parent.owner

        if action == 'view':
            has_item_permission = user.has_perm('view_itema', item) or user.has_perm('app.view_itema')
        elif action == 'change':
            has_item_permission = user.has_perm('change_itema', item) or user.has_perm('app.change_itema')


        return has_delegated_owner_permission or has_delegated_django_permission or has_item_permission

    def get_perms(self):
        return perms3