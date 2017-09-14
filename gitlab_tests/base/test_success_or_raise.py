from mock import Mock

import requests
from requests.exceptions import HTTPError

from gitlab_tests.base_test import BaseTest

from response_data.users import post_users_error


class TestSuccessOrRaise(BaseTest):
    def test_success_or_raise_without_error(self):
        response = Mock()
        response_config = {
            'status_code': 200,
            'json.return_value': post_users_error
        }
        response.configure_mock(**response_config)

        self.gitlab.success_or_raise(response, [200])

    def test_success_or_raise_with_error(self):
        response = requests.models.Response()
        response.status_code = 400
        response._content = post_users_error

        self.gitlab.suppress_http_error = False
        self.assertRaises(HTTPError, self.gitlab.success_or_raise, response)
        self.gitlab.suppress_http_error = True
