import responses
from requests.exceptions import HTTPError

from gitlab_tests.base_test import BaseTest
from response_data.deploy_keys import *


class TestGetAllDeployKeys(BaseTest):
    @responses.activate
    def test_get_all_deploy_keys(self):
        responses.add(
            responses.GET,
            self.gitlab.api_url + '/deploy_keys',
            json=get_deploy_keys,
            status=200,
            content_type='application/json')

        self.assertEqual(get_deploy_keys, self.gitlab.get_all_deploy_keys())

    @responses.activate
    def test_get_all_deploy_keys_empty_list(self):
        responses.add(
            responses.GET,
            self.gitlab.api_url + '/deploy_keys',
            json=[],
            status=200,
            content_type='application/json')

        self.assertEqual([], self.gitlab.get_all_deploy_keys())

    @responses.activate
    def test_get_all_deploy_keys_exception(self):
        responses.add(
            responses.GET,
            self.gitlab.api_url + '/deploy_keys',
            body='{"error":"404 Not Found"}',
            status=404,
            content_type='application/json')

        self.gitlab.suppress_http_error = False
        self.assertRaises(HTTPError, self.gitlab.get_all_deploy_keys)
        self.gitlab.suppress_http_error = True


class TestEnableDeployKeys(BaseTest):
    @responses.activate
    def test_enable_deploy_key(self):
        responses.add(
            responses.POST,
            self.gitlab.api_url + '/projects/5/deploy_keys/1/enable',
            json=get_deploy_keys[0],
            status=201,
            content_type='application/json')

        self.assertEqual(get_deploy_keys[0], self.gitlab.enable_deploy_key(5, 1))

    @responses.activate
    def test_enable_deploy_key_exception(self):
        responses.add(
            responses.POST,
            self.gitlab.api_url + '/projects/5/deploy_keys/2/enable',
            body='{"message": "500 Internal Server Error"}',
            status=500,
            content_type='application/json')

        self.gitlab.suppress_http_error = False
        self.assertRaises(HTTPError, self.gitlab.enable_deploy_key, 5, 2)
        self.gitlab.suppress_http_error = True
