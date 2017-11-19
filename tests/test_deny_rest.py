# noinspection PyPackageRequirements

import pytest

from tests.test_item_base import BaseTestDenyAllItems
from tests.test_item_rest_base import BaseTestItemRest
from tests.test_users_base import BaseUsers


@pytest.mark.django_db(transaction=True)
class TestDenyRest(BaseTestDenyAllItems, BaseTestItemRest, BaseUsers):

    def transform_expected_result_code(self, expected_result_code,
                                       client, request, user, read, write,
                                       guardian_read, guardian_write,
                                       item_read, item_write, guardian_item_read,
                                       guardian_item_write,
                                       action, item_class):
        return 404