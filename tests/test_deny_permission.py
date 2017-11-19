# noinspection PyPackageRequirements

import pytest

from tests.app.viewsets import perms1
from tests.test_item_base import BaseTestDenyAllItems
from tests.test_item_permission_base import BaseTestItemPermission
from tests.test_users_base import BaseUsers


@pytest.mark.django_db(transaction=True)
class TestDenyPermission(BaseTestDenyAllItems, BaseTestItemPermission, BaseUsers):

    def transform_should_be_allowed(self, *args):
        return False

    def get_perms(self):
        return perms1