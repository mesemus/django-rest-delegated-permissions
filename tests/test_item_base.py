import random

import pytest
from django.contrib.auth.models import Permission

from tests.test_users_base import BaseUsers
from .app.models import Container, ItemA, ItemB, ItemC, ItemD
from .test_item_querysets_base import BaseTestItemQuerySets


class BaseTestItemA:

    # region Common

    # noinspection PyAttributeOutsideInit
    @pytest.fixture(autouse=True)
    def environ(self):
        self.containers = []
        self.items = []
        self.guardian_items = []

        for i in range(5):
            container = Container.objects.create(name='container_%s' % i)
            for j in range(2):
                item = ItemA.objects.create(name='ItemA_%s_%s' % (i, j), parent=container)
                self.items.append(item)
                if i < 2:
                    self.guardian_items.append(item)

            self.containers.append(container)

        self.guardian_containers = self.containers[:2]

        self.view_permission = Permission.objects.get(codename='view_container')
        self.change_permission = Permission.objects.get(codename='change_container')

        self.view_item_permission = Permission.objects.get(codename='view_itema')
        self.change_item_permission = Permission.objects.get(codename='change_itema')

        # take 1/4 of items in A for guardian on items
        random.seed(0)
        self.guardian_directly_on_items = random.sample(self.items, len(self.items)//4)

    @pytest.fixture()
    def item_class(self):
        return ItemA

    def container_url(self, container):
        return '/container/%s/' % container.id

    def item_url(self, item):
        return '/item/A/%s/' % item.id

    # endregion


class BaseTestItemB:

    # region Common

    # noinspection PyAttributeOutsideInit
    @pytest.fixture(autouse=True)
    def environ(self):
        self.containers = []
        self.items = []
        self.guardian_items = []

        non_rights_container = Container.objects.create(name='non_rights')

        for i in range(5):
            container = Container.objects.create(name='container_%s' % i)
            for j in range(2):
                item = ItemB.objects.create(name='ItemB_%s_%s' % (i, j))
                item.parents.add(container)
                item.parents.add(non_rights_container)
                self.items.append(item)
                if i < 2:
                    self.guardian_items.append(item)

            self.containers.append(container)

        self.guardian_containers = self.containers[:2]

        self.view_permission = Permission.objects.get(codename='view_container')
        self.change_permission = Permission.objects.get(codename='change_container')

        self.view_item_permission = Permission.objects.get(codename='view_itemb')
        self.change_item_permission = Permission.objects.get(codename='change_itemb')

        # take 1/4 of items in A for guardian on items
        self.guardian_directly_on_items = random.sample(self.items, len(self.items)//4)

    @pytest.fixture()
    def item_class(self):
        return ItemB

    def container_url(self, container):
        return '/container/%s/' % container.id

    def item_url(self, item):
        return '/item/B/%s/' % item.id

    # endregion


class BaseTestItemC:

    # region Common

    # noinspection PyAttributeOutsideInit
    @pytest.fixture(autouse=True)
    def environ(self):
        self.containers = []
        self.items = []
        self.guardian_items = []

        Container.objects.create(name='no_item_c')

        for i in range(5):
            item = ItemC.objects.create(name='ItemC_%s' % (i,))
            container = Container.objects.create(name='container_%s' % i, item_c=item)
            self.items.append(item)
            if i < 2:
                self.guardian_items.append(item)

            self.containers.append(container)

        self.guardian_containers = self.containers[:2]

        self.view_permission = Permission.objects.get(codename='view_container')
        self.change_permission = Permission.objects.get(codename='change_container')

        self.view_item_permission = Permission.objects.get(codename='view_itemc')
        self.change_item_permission = Permission.objects.get(codename='change_itemc')

        # take 1/4 of items in A for guardian on items
        self.guardian_directly_on_items = random.sample(self.items, len(self.items)//4)

    @pytest.fixture()
    def item_class(self):
        return ItemC

    def container_url(self, container):
        return '/container/%s/' % container.id

    def item_url(self, item):
        return '/item/C/%s/' % item.id

    # endregion


class BaseTestItemD(BaseTestItemQuerySets, BaseUsers):

    # region Common

    # noinspection PyAttributeOutsideInit
    @pytest.fixture(autouse=True)
    def environ(self):
        self.containers = []
        self.items = []
        self.guardian_items = []

        non_rights_container = Container.objects.create(name='non_rights')

        for i in range(5):
            container = Container.objects.create(name='container_%s' % i)
            for j in range(2):
                item = ItemD.objects.create(name='ItemD_%s_%s' % (i, j))
                item.containers.add(container)
                item.containers.add(non_rights_container)
                self.items.append(item)
                if i < 2:
                    self.guardian_items.append(item)

            self.containers.append(container)

        self.guardian_containers = self.containers[:2]

        self.view_permission = Permission.objects.get(codename='view_container')
        self.change_permission = Permission.objects.get(codename='change_container')

        self.view_item_permission = Permission.objects.get(codename='view_itemd')
        self.change_item_permission = Permission.objects.get(codename='change_itemd')

        # take 1/4 of items in A for guardian on items
        self.guardian_directly_on_items = random.sample(self.items, len(self.items)//4)

    @pytest.fixture()
    def item_class(self):
        return ItemD

    def container_url(self, container):
        return '/container/%s/' % container.id

    def item_url(self, item):
        return '/item/D/%s/' % item.id

    # endregion
