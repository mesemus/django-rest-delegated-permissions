# noinspection PyPackageRequirements

import pytest

from tests.test_item_base import BaseTestItemA
from tests.test_users_base import BaseUsers
from .test_item_querysets_base import BaseTestItemQuerySets


@pytest.mark.django_db(transaction=True)
class TestItemAQuerySets(BaseTestItemA, BaseTestItemQuerySets, BaseUsers):
    pass