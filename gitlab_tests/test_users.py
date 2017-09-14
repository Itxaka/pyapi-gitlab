import responses
from requests.exceptions import HTTPError

from gitlab_tests.base_test import BaseTest
from response_data.users import *


class TestGetUsers(BaseTest):
    @responses.activate
    def test_get_users(self):
        responses.add(
            responses.GET,
            self.gitlab.api_url + '/users',
            match_querystring=False,
            json=get_users,
            status=200,
            content_type='application/json')

        self.assertEqual(get_users, self.gitlab.get_users())
        self.assertEqual(get_users, self.gitlab.get_users(search='test'))
        self.assertEqual(get_users, self.gitlab.getusers())

    @responses.activate
    def test_get_users_exception(self):
        responses.add(
            responses.GET,
            self.gitlab.api_url + '/users',
            match_querystring=False,
            json='{"error": "Not found"}',
            status=404,
            content_type='application/json')

        self.gitlab.suppress_http_error = False
        self.assertRaises(HTTPError, self.gitlab.get_users)
        self.gitlab.suppress_http_error = True
        self.assertEqual(False, self.gitlab.getusers())


class TestDeleteUser(BaseTest):
    @responses.activate
    def test_delete_user(self):
        responses.add(
            responses.DELETE,
            self.gitlab.api_url + '/users/14',
            json=delete_user,
            status=204,
            content_type='application/json')

        self.assertEqual(delete_user, self.gitlab.delete_user(14))
        self.assertTrue(self.gitlab.deleteuser(14))

    @responses.activate
    def test_get_users_exception(self):
        responses.add(
            responses.DELETE,
            self.gitlab.api_url + '/users/14',
            body='{"error": "Not found"}',
            status=404,
            content_type='application/json')

        self.gitlab.suppress_http_error = False
        self.assertRaises(HTTPError, self.gitlab.delete_user, 14)
        self.gitlab.suppress_http_error = True
        self.assertFalse(self.gitlab.deleteuser(14))
