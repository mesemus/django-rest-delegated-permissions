# noinspection PyPackageRequirements

import pytest

from tests.app.viewsets import perms1
from tests.test_item_base import BaseTestItemA, BaseTestDenyAllItems
from tests.test_users_base import BaseUsers
from .test_item_querysets_base import BaseTestItemQuerySets


@pytest.mark.django_db(transaction=True)
class TestDenyQuerySets(BaseTestDenyAllItems, BaseTestItemQuerySets, BaseUsers):

    def transform_expected_ids(self, *args):
        # deny all
        return set()

    def get_perms(self):
        return perms1