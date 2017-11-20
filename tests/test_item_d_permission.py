# noinspection PyPackageRequirements

import pytest

from tests.test_item_base import BaseTestItemA, BaseTestItemD
from tests.test_item_permission_base import BaseTestItemPermission, SelectiveBaseTestItemPermission
from tests.test_users_base import BaseUsers
from .test_item_querysets_base import BaseTestItemQuerySets


@pytest.mark.django_db(transaction=True)
# class TestItemDPermission(BaseTestItemD, BaseTestItemPermission, BaseUsers):
class TestItemDPermission(BaseTestItemD, SelectiveBaseTestItemPermission, BaseUsers):
    pass