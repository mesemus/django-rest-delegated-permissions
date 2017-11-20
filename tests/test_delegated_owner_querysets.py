# noinspection PyPackageRequirements

import pytest
from guardian.shortcuts import get_objects_for_user

from tests.app.models import ItemE, ItemA, Container
from tests.app.viewsets import perms2, perms3
from tests.test_item_base import BaseTestAllowOnlyOwner, BaseTestDelegatedOwner
from tests.test_users_base import BaseUsers
from .test_item_querysets_base import BaseTestItemQuerySets


@pytest.mark.django_db(transaction=True)
class TestDelegatedOwnerQuerySets(BaseTestDelegatedOwner, BaseTestItemQuerySets, BaseUsers):

    def transform_expected_ids(self, expected_ids, request):
        user = request.getfixturevalue('user')
        returned_set = set(ItemA.objects.filter(parent__owner=user))

        action = request.getfixturevalue('action')
        if action == 'view':
            if user.has_perm('app.view_container'):
                returned_set.update(ItemA.objects.filter(parent__owner__isnull=False))
            returned_set.update(
                ItemA.objects.filter(parent__in= get_objects_for_user(user, 'view_container', Container))
            )
        elif action == 'change':
            if user.has_perm('app.change_container'):
                returned_set.update(ItemA.objects.filter(parent__owner__isnull=False))
            returned_set.update(
                ItemA.objects.filter(parent__in= get_objects_for_user(user, 'change_container', Container))
            )

        if action == 'view':
            if user.has_perm('app.view_itema'):
                returned_set.update(ItemA.objects.all())
            returned_set.update(
                get_objects_for_user(user, 'view_itema', ItemA))
        elif action == 'change':
            if user.has_perm('app.change_itema'):
                returned_set.update(ItemA.objects.all())
            returned_set.update(
                get_objects_for_user(user, 'change_itema', ItemA))

        return set(x.id for x in returned_set)

    def get_perms(self):
        return perms3
