# noinspection PyPackageRequirements

import pytest

from tests.test_item_base import BaseTestDenyAllItems
from tests.test_item_permission_base import BaseTestItemPermission
from tests.test_users_base import BaseUsers


@pytest.mark.django_db(transaction=True)
class TestDenyPermission(BaseTestDenyAllItems, BaseTestItemPermission, BaseUsers):

    def transform_should_be_allowed(self, should_be_allowed, user, read, write, guardian_read, guardian_write,
                                    item_read, item_write, guardian_item_read, guardian_item_write, action, item_class):
        return False