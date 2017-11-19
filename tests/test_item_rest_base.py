# noinspection PyPackageRequirements
import json

import pytest


class BaseTestItemRest:
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
    def test_item_rest(self, client, request, user, read, write, guardian_read, guardian_write,
                       item_read, item_write, guardian_item_read, guardian_item_write,
                       action, item_class):

        if not user.is_anonymous:
            client.force_login(user)

        for c in item_class.objects.all():

            resource_url = self.item_url(c)

            expected_read_code = 404

            if read or item_read:
                expected_read_code = 200
            elif guardian_read and self.get_parents(c).intersection(set(self.guardian_containers)):
                expected_read_code = 200
            elif guardian_item_read and c in self.guardian_directly_on_items:
                expected_read_code = 200

            if action == 'view':
                resp = client.get(resource_url)
                expected_result_code = expected_read_code
            elif action == 'change':
                resp = client.patch(resource_url, json.dumps({}), content_type='application/json')
                if expected_read_code == 200:
                    expected_result_code = 403
                    if write or item_write:
                        expected_result_code = 200
                    elif guardian_write and self.get_parents(c).intersection(set(self.guardian_containers)):
                        expected_result_code = 200
                    elif guardian_item_write and c in self.guardian_directly_on_items:
                        expected_result_code = 200
                else:
                    expected_result_code = 404
            else:
                raise NotImplementedError('Action %s is not implemented in test' % action)

            expected_result_code = self.transform_expected_result_code(expected_result_code, request, c)

            assert resp.status_code == expected_result_code, \
                "The item had id %s, parents %s, the ids of guardian containers were %s, " \
                "the ids of direct guardian items was %s" % (
                    c.id,
                    [x.id for x in self.get_parents(c)],
                    [x.id for x in self.guardian_containers],
                    [x.id for x in self.guardian_directly_on_items],
                )

    def transform_expected_result_code(self, expected_result_code, request, item):
        return expected_result_code

    # endregion

    def get_parents(self, x):
        try:
            return set([x.parent])
        except:
            pass

        try:
            return set(x.container.all())
        except:
            pass

        try:
            return set(x.parents.all())
        except:
            pass

        return set(x.containers.all())
