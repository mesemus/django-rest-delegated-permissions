# noinspection PyPackageRequirements

import pytest

from tests.test_item_base import BaseTestItemB
from tests.test_item_permission_base import BaseTestItemPermission
from tests.test_item_rest_base import BaseTestItemRest
from tests.test_users_base import BaseUsers


@pytest.mark.django_db(transaction=True)
class TestItemBRest(BaseTestItemB, BaseTestItemRest, BaseUsers):
    pass