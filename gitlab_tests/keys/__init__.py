import responses
from requests.exceptions import HTTPError

from gitlab_tests.base_test import BaseTest
from response_data import not_found
from response_data.keys import get_keys


class TestKeys(BaseTest):
    @responses.activate
    def test_keys(self):
        responses.add(
            responses.GET,
            self.gitlab.api_url + '/keys/1',
            json=get_keys,
            status=201,
            content_type='application/json'
        )

        self.assertEqual(
            self.gitlab.keys(1),
            get_keys
        )

        self.assertEqual(
            self.gitlab.getsshkey(1),
            get_keys
        )

    @responses.activate
    def test_keys_with_bad_data(self):
        responses.add(
            responses.GET,
            self.gitlab.api_url + '/keys/1',
            json=not_found,
            status=404,
            content_type='application/json'
        )

        self.assertRaises(
            HTTPError,
            self.gitlab.keys, 1
        )

        # Don't raise exception when suppress http error is True
        self.gitlab.suppress_http_error = True
        self.assertFalse(self.gitlab.keys(1))

        # Deprecated version test
        self.assertFalse(self.gitlab.getsshkey(1))
        self.gitlab.suppress_http_error = False
