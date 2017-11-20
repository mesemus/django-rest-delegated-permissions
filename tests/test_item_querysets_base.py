# noinspection PyPackageRequirements

import pytest
from django.db.models.query import EmptyResultSet

from .app.viewsets import perms


class BaseTestItemQuerySets:

    # region Tests

    @pytest.mark.matrix(
        names=['guardian_read', 'guardian_write', 'guardian_item_read', 'guardian_item_write',
               'read', 'write', 'item_read', 'item_write', 'action'],
        combs=[
            {
                'guardian_read': ['true', 'false'],
                'guardian_write': ['true', 'false'],
                'guardian_item_read': ['true', 'false'],
                'guardian_item_write': ['true', 'false'],
                'read': ['true', 'false'],
                'write': ['true', 'false'],
                'item_read': ['true', 'false'],
                'item_write': ['true', 'false'],
                'action': [
                    'view', 'change'
                ]
            },
        ])
    def test_item_queryset(self, request, user, read, write, guardian_read, guardian_write,
                            item_read, item_write, guardian_item_read, guardian_item_write,
                            action, item_class):
        self._do_test(action, guardian_item_read, guardian_item_write, guardian_read, guardian_write, item_class,
                      item_read, item_write, read, request, user, write)

    def _do_test(self, action, guardian_item_read, guardian_item_write, guardian_read, guardian_write, item_class,
                 item_read, item_write, read, request, user, write):
        qs = self.get_perms().create_queryset_factory(item_class)(user, action)
        print("\nOutput from %s" % request.node.name)
        try:
            print(qs.query)
        except EmptyResultSet:
            print('{empty}')
        ids = set(qs.values_list('id', flat=True))
        expected_ids = set()
        # guardian_write_true
        # guardian_item_write_true
        if action == 'view':
            if read:
                expected_ids.update(x.id for x in self.items)
            if guardian_read:
                expected_ids.update(x.id for x in self.guardian_items)
            if item_read:
                expected_ids.update(x.id for x in self.items)
            if guardian_item_read:
                expected_ids.update(x.id for x in self.guardian_directly_on_items)
        elif action == 'change':
            if write:
                expected_ids.update(x.id for x in self.items)
            if guardian_write:
                expected_ids.update(x.id for x in self.guardian_items)
            if item_write:
                expected_ids.update(x.id for x in self.items)
            if guardian_item_write:
                expected_ids.update(x.id for x in self.guardian_directly_on_items)
        expected_ids = self.transform_expected_ids(expected_ids, request)
        assert ids == expected_ids, ''

    def get_perms(self):
        return perms

    def transform_expected_ids(self, expected_ids, request):
        return expected_ids

    # endregion


class SelectiveBaseTestItemQuerySets(BaseTestItemQuerySets):

    @pytest.mark.matrix(
        names=['guardian_read', 'guardian_write', 'guardian_item_read', 'guardian_item_write',
               'read', 'write', 'item_read', 'item_write', 'action'],
        combs=[
            {
                'guardian_read': ['true', 'false'],
                'guardian_write': ['true', 'false'],
                'guardian_item_read': ['false'],
                'guardian_item_write': ['false'],
                'read': ['true', 'false'],
                'write': ['true', 'false'],
                'item_read': ['false'],
                'item_write': ['false'],
                'action': [
                    'view', 'change'
                ]
            },
        ])
    def test_item_queryset(self, request, user, read, write, guardian_read, guardian_write,
                            item_read, item_write, guardian_item_read, guardian_item_write,
                            action, item_class):
        self._do_test(action, guardian_item_read, guardian_item_write, guardian_read, guardian_write, item_class,
                      item_read, item_write, read, request, user, write)
