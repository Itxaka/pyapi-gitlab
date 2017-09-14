import responses
from requests.exceptions import HTTPError

from gitlab_tests.base_test import BaseTest
from response_data.users import *


class TestDelete(BaseTest):
    @responses.activate
    def test_delete(self):
        responses.add(
            responses.DELETE,
            self.gitlab.api_url + '/users/5',
            json=None,
            status=204,
            content_type='application/json')

        self.assertEqual({}, self.gitlab.delete('/users/5'))
        self.assertEqual({}, self.gitlab.delete('/users/5', default_response={}))

    @responses.activate
    def test_delete_404(self):
        responses.add(
            responses.POST,
            self.gitlab.api_url + '/users',
            body=post_users_error,
            status=409,
            content_type='application/json')

        self.gitlab.suppress_http_error = False
        self.assertRaises(HTTPError, self.gitlab.post, '/users')
        self.gitlab.suppress_http_error = True