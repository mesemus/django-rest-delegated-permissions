# noinspection PyPackageRequirements
import random

import pytest
from django.contrib.auth.models import Permission

from .app.models import Container, ItemC
from .test_item_querysets_base import BaseTestItemQuerySets


@pytest.mark.django_db(transaction=True)
class TestQuerySets(BaseTestItemQuerySets):

    # region Common

    # noinspection PyAttributeOutsideInit
    @pytest.fixture(autouse=True)
    def environ(self):
        self.containers = []
        self.items = []
        self.guardian_items = []

        Container.objects.create(name='no_item_c')

        for i in range(10):
            item = ItemC.objects.create(name='ItemC_%s' % (i,))
            container = Container.objects.create(name='container_%s' % i, item_c=item)
            self.items.append(item)
            if i < 5:
                self.guardian_items.append(item)

            self.containers.append(container)

        self.guardian_containers = self.containers[:5]

        self.view_permission = Permission.objects.get(codename='view_container')
        self.change_permission = Permission.objects.get(codename='change_container')

        self.view_item_permission = Permission.objects.get(codename='view_itemc')
        self.change_item_permission = Permission.objects.get(codename='change_itemc')

        # take 1/4 of items in A for guardian on items
        self.guardian_directly_on_items = random.sample(self.items, len(self.items)//4)

    @pytest.fixture()
    def item_class(self):
        return ItemC

    # endregion
