from integration_tests.base import BaseTest, log_to_term
from response_data.users import *


class TestGitlabV91(BaseTest):
    def test_add_remove_user(self):
        """Add and remove a user"""
        response = self.gitlab.createuser(
            'test', 'test', 'TestPassword1', 'test@example.com')
        self.assertEqual(post_users.keys(), response.keys())

        response = self.gitlab.delete_user(response['id'])
        self.assertTrue(isinstance(response, dict))
        self.assertEqual({}, response)
