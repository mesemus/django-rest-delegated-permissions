# noinspection PyPackageRequirements

import pytest

from tests.app.viewsets import perms2
from tests.test_item_base import BaseTestAllowOnlyOwner
from tests.test_item_permission_base import BaseTestItemPermission
from tests.test_users_base import BaseUsers


@pytest.mark.django_db(transaction=True)
class TestAllowOnlyOwnerPermission(BaseTestAllowOnlyOwner, BaseTestItemPermission, BaseUsers):

    def transform_should_be_allowed(self, should_be_allowed, request, item):
        return request.getfixturevalue('user') == item.owner

    def get_perms(self):
        return perms2