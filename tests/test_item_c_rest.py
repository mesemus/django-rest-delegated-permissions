# noinspection PyPackageRequirements

import pytest

from tests.test_item_base import BaseTestItemA, BaseTestItemC
from tests.test_item_permission_base import BaseTestItemPermission
from tests.test_item_rest_base import BaseTestItemRest
from tests.test_users_base import BaseUsers
from .test_item_querysets_base import BaseTestItemQuerySets


@pytest.mark.django_db(transaction=True)
class TestItemCRest(BaseTestItemC, BaseTestItemRest, BaseUsers):
    pass