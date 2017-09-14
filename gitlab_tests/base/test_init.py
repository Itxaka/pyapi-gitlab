from gitlab import Gitlab
from gitlab_tests.base_test import BaseTest


class TestInit(BaseTest):
    def test___init__with_token(self):
        gitlab = Gitlab('http://localhost:10080', verify_ssl=False, token='something')
        self.assertEqual('something', gitlab.token)
        self.assertEqual({'PRIVATE-TOKEN': 'something'}, gitlab.headers)

    def test___init__with_oauth_token(self):
        gitlab = Gitlab('http://localhost:10080', verify_ssl=False, oauth_token='something')
        self.assertEqual('something', gitlab.oauth_token)
        self.assertEqual({'Authorization': 'Bearer something'}, gitlab.headers)

    def test___init__without_host(self):
        self.assertRaises(ValueError, Gitlab, None, verify_ssl=False, oauth_token='something')

    def test___init__without_protocol(self):
        gitlab = Gitlab('localhost:10080', verify_ssl=False, oauth_token='something')
        self.assertEqual('https://localhost:10080', gitlab.host)

    def test___init__with_https(self):
        gitlab = Gitlab('https://localhost:10080', verify_ssl=False, oauth_token='something')
        self.assertEqual('https://localhost:10080', gitlab.host)