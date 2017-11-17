# noinspection PyPackageRequirements
import random

import pytest
from django.contrib.auth.models import Permission

from .app.models import Container, ItemD
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

        non_rights_container = Container.objects.create(name='non_rights')

        for i in range(10):
            container = Container.objects.create(name='container_%s' % i)
            for j in range(2):
                item = ItemD.objects.create(name='ItemD_%s_%s' % (i, j))
                item.containers.add(container)
                item.containers.add(non_rights_container)
                self.items.append(item)
                if i < 5:
                    self.guardian_items.append(item)

            self.containers.append(container)

        self.guardian_containers = self.containers[:5]

        self.view_permission = Permission.objects.get(codename='view_container')
        self.change_permission = Permission.objects.get(codename='change_container')

        self.view_item_permission = Permission.objects.get(codename='view_itemd')
        self.change_item_permission = Permission.objects.get(codename='change_itemd')

        # take 1/4 of items in A for guardian on items
        self.guardian_directly_on_items = random.sample(self.items, len(self.items)//4)

    @pytest.fixture()
    def item_class(self):
        return ItemD

    # endregion
