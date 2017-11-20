# noinspection PyPackageRequirements

import pytest

from tests.test_item_base import BaseTestItemB
from tests.test_item_permission_base import BaseTestItemPermission, SelectiveBaseTestItemPermission
from tests.test_users_base import BaseUsers


@pytest.mark.django_db(transaction=True)
# class TestItemBPermission(BaseTestItemB, BaseTestItemPermission, BaseUsers):
class TestItemBPermission(BaseTestItemB, SelectiveBaseTestItemPermission, BaseUsers):
    pass