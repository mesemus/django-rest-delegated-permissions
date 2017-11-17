# noinspection PyPackageRequirements

import pytest

from tests.test_item_base import BaseTestItemC
from tests.test_users_base import BaseUsers
from .test_item_querysets_base import BaseTestItemQuerySets


@pytest.mark.django_db(transaction=True)
class TestItemCQuerySets(BaseTestItemC, BaseTestItemQuerySets, BaseUsers):
    pass