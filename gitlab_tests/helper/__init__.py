from unittest import TestCase
from gitlab.helper import format_string


class TestFormatString(TestCase):
    def test__format_string(self):
        self.assertEqual('foo%2Fbar', format_string('foo/bar'))
        self.assertEqual(1, format_string(1))
