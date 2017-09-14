import responses
from requests.exceptions import HTTPError

from gitlab_tests.base_test import BaseTest
from response_data.tags import *


class TestDeleteRepositoryTag(BaseTest):
    @responses.activate
    def test_delete_repository_tag(self):
        responses.add(
            responses.DELETE,
            self.gitlab.api_url + '/projects/5/repository/tags/test',
            json=delete_repository_tag,
            status=200,
            content_type='application/json')

        self.assertEqual(delete_repository_tag, self.gitlab.delete_repository_tag(5, 'test'))

    @responses.activate
    def test_delete_repository_tag_exception(self):
        responses.add(
            responses.DELETE,
            self.gitlab.api_url + '/projects/5/repository/tags/test',
            json='{"message":"No such tag"}',
            status=404,
            content_type='application/json')

        self.gitlab.suppress_http_error = False
        self.assertRaises(HTTPError, self.gitlab.delete_repository_tag, 5, 'test')
        self.gitlab.suppress_http_error = True
