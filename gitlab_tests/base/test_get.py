from requests.exceptions import HTTPError
import responses

from gitlab_tests.base_test import BaseTest
from response_data.users import get_users


class TestGet(BaseTest):
    @responses.activate
    def test_get_with_200(self):
        responses.add(
            responses.GET,
            self.gitlab.api_url + '/users',
            json=get_users,
            status=200,
            content_type='application/json')

        self.assertEqual(get_users, self.gitlab.get('/users'))
        self.assertEqual(get_users, self.gitlab.get('/users', default_response={}))

    @responses.activate
    def test_get_with_404(self):
        responses.add(
            responses.GET,
            self.gitlab.api_url + '/users',
            body='{"error": "Not here"}',
            status=404,
            content_type='application/json')

        self.gitlab.suppress_http_error = False
        self.assertRaises(HTTPError, self.gitlab.get, '/users')
        self.gitlab.suppress_http_error = True

