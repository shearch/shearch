"""
This tests data_json command retrieval module.
"""

# http://openp2p.com/pub/a/python/2004/12/02/tdd_pyunit.html
# http://onlamp.com/pub/a/python/2005/02/03/tdd_pyunit2.html
# http://docs.python.org/2/library/unittest.html

import unittest

import data_json

class TestDataJSON(unittest.TestCase):

    def test_get_commands_empty(self):
        self.assertEqual(
            data_json.get_commands(['']),
            [],
            'Querying command base without tags should return empty array.'
        )

    def test_get_commands_git(self):
        self.assertEqual(
            data_json.get_commands(['git']),
            [{u'tag': [u'git', u'status'], u'command': u'git status', u'description': u'Returns git status.'}],
            'Database did not return expected item for "git" tag.'
        )

    def test_get_commands_git_status(self):
        self.assertEqual(
            data_json.get_commands(['git', 'status']),
            [{u'tag': [u'git', u'status'], u'command': u'git status', u'description': u'Returns git status.'}],
            'Database did not return expected item for "git, status" tags.'
        )

    def test_get_commands_status(self):
        self.assertEqual(
            data_json.get_commands(['status']),
            [{u'tag': [u'hg', u'mercurial', u'status'], u'command': u'hg status', u'description': u'Returns hg status.'}, {u'tag': [u'git', u'status'], u'command': u'git status', u'description': u'Returns git status.'}],
            'Database did not return expected item for "status" tag.'
        )

def main():
    unittest.main()

if __name__ == '__main__':
    main()