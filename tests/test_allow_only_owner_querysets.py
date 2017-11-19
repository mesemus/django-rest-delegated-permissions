# noinspection PyPackageRequirements

import pytest

from tests.app.models import ItemE
from tests.app.viewsets import perms2
from tests.test_item_base import BaseTestAllowOnlyOwner
from tests.test_users_base import BaseUsers
from .test_item_querysets_base import BaseTestItemQuerySets


@pytest.mark.django_db(transaction=True)
class TestDenyQuerySets(BaseTestAllowOnlyOwner, BaseTestItemQuerySets, BaseUsers):

    def transform_expected_ids(self, expected_ids, request):
        user = request.getfixturevalue('user')
        return set(ItemE.objects.filter(owner=user).values_list('id', flat=True))

    def get_perms(self):
        return perms2
