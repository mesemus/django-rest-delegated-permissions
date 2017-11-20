# noinspection PyPackageRequirements

import pytest

from tests.test_item_base import BaseTestItemD
from tests.test_users_base import BaseUsers
from .test_item_querysets_base import BaseTestItemQuerySets, SelectiveBaseTestItemQuerySets


@pytest.mark.django_db(transaction=True)
# class TestItemDQuerySets(BaseTestItemD, BaseTestItemQuerySets, BaseUsers):
class TestItemDQuerySets(BaseTestItemD, SelectiveBaseTestItemQuerySets, BaseUsers):
    pass
