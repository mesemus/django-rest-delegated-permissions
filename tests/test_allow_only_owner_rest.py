# noinspection PyPackageRequirements

import pytest

from tests.test_item_base import BaseTestDenyAllItems, BaseTestAllowOnlyOwner
from tests.test_item_rest_base import BaseTestItemRest
from tests.test_users_base import BaseUsers


@pytest.mark.django_db(transaction=True)
class TestAllowOnlyOwnerRest(BaseTestAllowOnlyOwner, BaseTestItemRest, BaseUsers):

    def transform_expected_result_code(self, expected_result_code, request, item):
        if item.owner != request.getfixturevalue('user'):
            return 404
        return 200