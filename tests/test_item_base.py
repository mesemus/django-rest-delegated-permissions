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
        self.items = []
        self.guardian_items = []
        self.guardian_directly_on_items = []
        self.containers = []
        self.guardian_containers = []

        for guardian_container in (0, 1):
            container = Container.objects.create(name='container_%s' % guardian_container)
            self.containers.append(container)
            if guardian_container:
                self.guardian_containers.append(container)
            for guardian_directly_on_item in (0, 1):
                item = ItemA.objects.create(name='ItemA_%s_%s' %
                                                 (guardian_container, guardian_directly_on_item),
                                            parent=container)
                self.items.append(item)
                if guardian_container:
                    self.guardian_items.append(item)
                if guardian_directly_on_item:
                    self.guardian_directly_on_items.append(item)

        self.view_permission = Permission.objects.get(codename='view_container')
        self.change_permission = Permission.objects.get(codename='change_container')

        self.view_item_permission = Permission.objects.get(codename='view_itema')
        self.change_item_permission = Permission.objects.get(codename='change_itema')

    @pytest.fixture()
    def item_class(self):
        return ItemA

    def item_url(self, item):
        return '/item/A/%s/' % item.id

    # endregion


class BaseTestItemB:

    # region Common

    # noinspection PyAttributeOutsideInit
    @pytest.fixture(autouse=True)
    def environ(self):
        non_rights_container = Container.objects.create(name='non_rights')

        self.items = []
        self.guardian_items = []
        self.guardian_directly_on_items = []
        self.containers = []
        self.guardian_containers = []

        for guardian_container in (0, 1):
            container = Container.objects.create(name='container_%s' % guardian_container)
            self.containers.append(container)
            if guardian_container:
                self.guardian_containers.append(container)
            for guardian_directly_on_item in (0, 1):
                item = ItemB.objects.create(name='ItemB_%s_%s' %
                                                 (guardian_container, guardian_directly_on_item))
                item.parents.add(container)
                item.parents.add(non_rights_container)
                self.items.append(item)
                if guardian_container:
                    self.guardian_items.append(item)
                if guardian_directly_on_item:
                    self.guardian_directly_on_items.append(item)

        self.view_permission = Permission.objects.get(codename='view_container')
        self.change_permission = Permission.objects.get(codename='change_container')

        self.view_item_permission = Permission.objects.get(codename='view_itemb')
        self.change_item_permission = Permission.objects.get(codename='change_itemb')

    @pytest.fixture()
    def item_class(self):
        return ItemB

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
        self.guardian_containers = []

        Container.objects.create(name='no_item_c')

        for i in range(4):
            item = ItemC.objects.create(name='ItemC_%s' % (i,))
            container = Container.objects.create(name='container_%s' % i, item_c=item)
            self.items.append(item)
            self.containers.append(container)
            if i < 2:
                self.guardian_items.append(item)
                self.guardian_containers.append(container)


        self.view_permission = Permission.objects.get(codename='view_container')
        self.change_permission = Permission.objects.get(codename='change_container')

        self.view_item_permission = Permission.objects.get(codename='view_itemc')
        self.change_item_permission = Permission.objects.get(codename='change_itemc')

        self.guardian_directly_on_items = [
            self.items[0],
            self.items[2]
        ]

    @pytest.fixture()
    def item_class(self):
        return ItemC

    def item_url(self, item):
        return '/item/C/%s/' % item.id

    # endregion


class BaseTestItemD:

    # region Common

    # noinspection PyAttributeOutsideInit
    @pytest.fixture(autouse=True)
    def environ(self):
        non_rights_container = Container.objects.create(name='non_rights')

        self.items = []
        self.guardian_items = []
        self.guardian_directly_on_items = []
        self.containers = []
        self.guardian_containers = []

        for guardian_container in (0, 1):
            container = Container.objects.create(name='container_%s' % guardian_container)
            self.containers.append(container)
            if guardian_container:
                self.guardian_containers.append(container)
            for guardian_directly_on_item in (0, 1):
                item = ItemD.objects.create(name='ItemD_%s_%s' %
                                                 (guardian_container, guardian_directly_on_item))
                item.containers.add(container)
                item.containers.add(non_rights_container)
                self.items.append(item)
                if guardian_container:
                    self.guardian_items.append(item)
                if guardian_directly_on_item:
                    self.guardian_directly_on_items.append(item)

        self.view_permission = Permission.objects.get(codename='view_container')
        self.change_permission = Permission.objects.get(codename='change_container')

        self.view_item_permission = Permission.objects.get(codename='view_itemd')
        self.change_item_permission = Permission.objects.get(codename='change_itemd')

    @pytest.fixture()
    def item_class(self):
        return ItemD

    def item_url(self, item):
        return '/item/D/%s/' % item.id

    # endregion


class BaseTestDenyAllItems:

    # region Common

    # noinspection PyAttributeOutsideInit
    @pytest.fixture(autouse=True)
    def environ(self):
        non_rights_container = Container.objects.create(name='non_rights')

        self.items = []
        self.guardian_items = []
        self.guardian_directly_on_items = []
        self.containers = []
        self.guardian_containers = []

        for guardian_container in (0, 1):
            container = Container.objects.create(name='container_%s' % guardian_container)
            self.containers.append(container)
            if guardian_container:
                self.guardian_containers.append(container)
            for guardian_directly_on_item in (0, 1):
                item = ItemD.objects.create(name='ItemD_%s_%s' %
                                                 (guardian_container, guardian_directly_on_item))
                item.containers.add(container)
                item.containers.add(non_rights_container)
                self.items.append(item)
                if guardian_container:
                    self.guardian_items.append(item)
                if guardian_directly_on_item:
                    self.guardian_directly_on_items.append(item)

        self.view_permission = Permission.objects.get(codename='view_container')
        self.change_permission = Permission.objects.get(codename='change_container')

        self.view_item_permission = Permission.objects.get(codename='view_itemd')
        self.change_item_permission = Permission.objects.get(codename='change_itemd')

    @pytest.fixture()
    def item_class(self):
        return ItemA

    def item_url(self, item):
        return '/item/deny/%s/' % item.id

    # endregion
