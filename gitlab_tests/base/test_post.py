import responses
from requests.exceptions import HTTPError

from gitlab_tests.base_test import BaseTest
from response_data.users import post_users, post_users_error


class TestPost(BaseTest):
    @responses.activate
    def test_post_with_201(self):
        responses.add(
            responses.POST,
            self.gitlab.api_url + '/users',
            json=post_users,
            status=201,
            content_type='application/json')
        data = {
            'name': 'test',
            'username': 'test1',
            'password': 'MyTestPassword1',
            'email': 'example@example.com'
        }

        self.assertEqual(post_users, self.gitlab.post('/users', **data))
        self.assertEqual(post_users, self.gitlab.post('/users', default_response={}, **data))

    @responses.activate
    def test_get_with_404(self):
        responses.add(
            responses.POST,
            self.gitlab.api_url + '/users',
            body=post_users_error,
            status=409,
            content_type='application/json')
        data = {
            'name': 'test',
            'username': 'test1',
            'password': 'MyTestPassword1',
            'email': 'example@example.com'
        }

        self.gitlab.suppress_http_error = False
        self.assertRaises(HTTPError, self.gitlab.post, '/users', **data)
        self.gitlab.suppress_http_error = True
