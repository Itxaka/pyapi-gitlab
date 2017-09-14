import responses
from gitlab_tests.base_test import BaseTest
from response_data.common import *
from response_data.users import *


class TestLogin(BaseTest):
    @responses.activate
    def test_login(self):
        responses.add(
            responses.POST,
            self.gitlab.api_url + '/session',
            json=login,
            status=201,
            content_type='application/json')

        self.assertEqual(
            login, self.gitlab.login(user=self.user, password=self.password))

    @responses.activate
    def test_login_email(self):
        responses.add(
            responses.POST,
            self.gitlab.api_url + '/session',
            json=login,
            status=201,
            content_type='application/json')

        self.assertEqual(
            login, self.gitlab.login(email='admin@example.com', password='test'))

    @responses.activate
    def test_login_with_no_values(self):
        responses.add(
            responses.POST,
            self.gitlab.api_url + '/session',
            body=get_users,
            status=404,
            content_type='application/json')
        self.assertRaises(ValueError, self.gitlab.login)
