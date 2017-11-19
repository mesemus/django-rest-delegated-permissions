# noinspection PyPackageRequirements

import pytest

from tests.test_item_base import BaseTestItemA, BaseTestDenyAllItems
from tests.test_users_base import BaseUsers
from .test_item_querysets_base import BaseTestItemQuerySets


@pytest.mark.django_db(transaction=True)
class TestDenyQuerySets(BaseTestDenyAllItems, BaseTestItemQuerySets, BaseUsers):

    def transform_expected_ids(self, expected_ids, request, user, read, write, guardian_read, guardian_write,
                            item_read, item_write, guardian_item_read, guardian_item_write,
                            action, item_class):
        # deny all
        return set()