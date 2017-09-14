import os
import unittest

import responses

from gitlab import Gitlab


class BaseTest(unittest.TestCase):
    @responses.activate
    def setUp(self):
        self.user = os.environ.get('gitlab_user', 'root')
        self.password = os.environ.get('gitlab_password', '5iveL!fe')
        self.host = os.environ.get('gitlab_host', 'http://localhost:10080')
        self.gitlab = Gitlab(host=self.host, verify_ssl=False, suppress_http_error=False)
        self.gitlab.host = self.host

        responses.add(
            responses.POST,
            self.gitlab.api_url + '/session',
            json={'private_token': 'test'},
            status=201,
            content_type='application/json')

        self.gitlab.login(user=self.user, password=self.password)
