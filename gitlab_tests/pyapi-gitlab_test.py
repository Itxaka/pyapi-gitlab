"""
pyapi-gitlab tests
"""

import unittest
import gitlab
import os
import time
import random
import string
try:
    from Crypto.PublicKey import RSA
    ssh_test = True
except ImportError:
    ssh_test = False

user = os.environ.get('gitlab_user', 'root')
password = os.environ.get('gitlab_password', 'roottoor')
host = os.environ.get('gitlab_host', 'http://localhost:8080')


class GitlabTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.git = gitlab.Gitlab(host=host)
        cls.git.login(user=user, password=password)
        name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        cls.project = cls.git.createproject(name=name, visibility_level="private",
                                            import_url="https://github.com/Itxaka/pyapi-gitlab.git")
        # wait a bit for the project to be fully imported
        time.sleep(5)
        cls.project_id = cls.project['id']
        cls.user_id = cls.git.currentuser()['id']

    @classmethod
    def tearDownClass(cls):
        cls.git.deleteproject(cls.project_id)

    def test_user(self):
        assert isinstance(self.git.createuser(name="test", username="test",
                                              password="test1234", email="test@test.com",
                                              skype="this", linkedin="that"), dict)
        # get all users
        assert isinstance(self.git.getusers(), list)  # compatible with 2.6
        assert isinstance(self.git.currentuser(), dict)
        user = self.git.getusers(search="test")[0]
        self.assertTrue(self.git.deleteuser(user["id"]))
        # check can_create_user
        user = self.git.createuser("random", "random", "random1234", "random@random.org",
                                   can_create_group="false")
        self.assertFalse(self.git.getuser(user['id'])['can_create_group'])
        self.git.deleteuser(user['id'])
        user = self.git.createuser("random", "random", "random1234", "random@random.org",
                                   can_create_group="true")
        self.assertTrue(self.git.getuser(user['id'])['can_create_group'])
        assert isinstance(self.git.edituser(user['id'], can_create_group="false"), dict)
        # Check that indeed the user details were changed
        self.assertFalse(self.git.getuser(user['id'])['can_create_group'])
        self.git.deleteuser(user['id'])
        # get X pages
        assert isinstance(self.git.getusers(page=2), list)  # compatible with 2.6
        assert isinstance(self.git.getusers(per_page=4), list)  # compatible with 2.6
        self.assertEqual(self.git.getusers(page=800), list(""))  # check against empty list
        self.assertTrue(self.git.getusers(per_page=43))  # check against false

    def test_project(self):
        # test project
        assert isinstance(self.git.getprojects(), list)
        assert isinstance(self.git.getprojects(page=5), list)
        assert isinstance(self.git.getprojects(per_page=7), list)
        assert isinstance(self.git.getproject(self.project_id), dict)
        self.assertFalse(self.git.getproject("wrong"))

        # test events
        assert isinstance(self.git.getprojectevents(self.project_id), list)
        assert isinstance(self.git.getprojectevents(self.project_id, page=3), list)
        assert isinstance(self.git.getprojectevents(self.project_id, per_page=4), list)

        # add-remove project members
        self.assertTrue(self.git.addprojectmember(id_=self.project_id, user_id=self.user_id, access_level="reporter", sudo=1))
        assert isinstance(self.git.listprojectmembers(id_=self.project_id), list)
        self.assertTrue(self.git.editprojectmember(id_=self.project_id, user_id=self.user_id, access_level="master", sudo=1))
        self.assertTrue(self.git.deleteprojectmember(id_=self.project_id, user_id=1))

        # Hooks testing
        self.assertTrue(self.git.addprojecthook(self.project_id, "http://web.com"))
        assert isinstance(self.git.getprojecthooks(self.project_id), list)
        assert isinstance(self.git.getprojecthook(self.project_id,
                                                  self.git.getprojecthooks(self.project_id)[0]['id']), dict)
        self.assertTrue(self.git.editprojecthook(self.project_id,
                                                 self.git.getprojecthooks(self.project_id)[0]['id'], "http://another.com"))
        self.assertTrue(self.git.deleteprojecthook(self.project_id,
                                                   self.git.getprojecthooks(self.project_id)[0]['id']))

    def test_branch(self):
        sha1 = self.git.listrepositorycommits(project_id=self.project_id)[0]["id"]
        assert isinstance(self.git.createbranch(id_=self.project_id, branch="deleteme", ref=sha1), dict)
        self.assertTrue(self.git.deletebranch(id_=self.project_id, branch="deleteme"))
        assert isinstance(self.git.listbranches(id_=self.project_id), list)
        assert isinstance(self.git.listbranch(id_=self.project_id, branch="develop"), dict)
        self.assertTrue(self.git.protectbranch(id_=self.project_id, branch="develop"))
        self.assertTrue(self.git.unprotectbranch(id_=self.project_id, branch="develop"))

    def test_sshkeys(self):
        assert isinstance(self.git.getsshkeys(), list)
        self.assertEquals(len(self.git.getsshkeys()), 0)
        # not working due a bug? in pycrypto: https://github.com/dlitz/pycrypto/issues/99
        """
        if ssh_test:
            name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            rsa_key = RSA.generate(1024)
            print(str(rsa_key.publickey().exportKey()))
            print(str(rsa_key.publickey().exportKey(format="OpenSSH")))
            self.assertTrue(self.git.addsshkey(title=name, key=str(rsa_key.publickey().exportKey())))
            self.assertGreater(self.git.getsshkeys(), 0)
            print(self.git.getsshkeys())
            key = self.git.getsshkeys()[0]
            self.git.deletesshkey(key["id"])"""

    def test_snippets(self):
        assert isinstance(self.git.createsnippet(self.project_id, "test", "test", "codeee"), dict)
        assert isinstance(self.git.getsnippets(self.project_id), list)
        snippet = self.git.getsnippets(self.project_id)[0]
        assert isinstance(self.git.getsnippet(self.project_id, snippet["id"]), dict)
        self.assertTrue(self.git.deletesnippet(self.project_id, snippet["id"]))

    def test_repositories(self):
        assert isinstance(self.git.getrepositories(self.project_id), list)
        assert isinstance(self.git.getrepositorybranch(self.project_id, "develop"), dict)
        assert isinstance(self.git.protectrepositorybranch(self.project_id, "develop"), dict)
        assert isinstance(self.git.unprotectrepositorybranch(self.project_id, "develop"), dict)
        assert isinstance(self.git.listrepositorytags(self.project_id), list)
        assert isinstance(self.git.listrepositorycommits(self.project_id), list)
        assert isinstance(self.git.listrepositorycommits(self.project_id, page=1), list)
        assert isinstance(self.git.listrepositorycommits(self.project_id, per_page=7), list)
        commit = self.git.listrepositorycommits(self.project_id)[0]
        assert isinstance(self.git.listrepositorycommit(self.project_id, commit["id"]), dict)
        assert isinstance(self.git.listrepositorycommitdiff(self.project_id, commit["id"]), list)
        assert isinstance(self.git.listrepositorytree(self.project_id), list)
        assert isinstance(self.git.listrepositorytree(self.project_id, path="docs"), list)
        assert isinstance(self.git.listrepositorytree(self.project_id, ref_name="develop"), list)
        assert isinstance(str(self.git.getrawblob(self.project_id, commit['id'], "setup.py")), str)
        commit = self.git.listrepositorycommits(self.project_id)
        assert isinstance(self.git.compare_branches_tags_commits(self.project_id,
                                                                 from_id=commit[1]["id"],
                                                                 to_id=commit[0]["id"]), dict)
        self.assertTrue(self.git.createfile(self.project_id, "test.file", "develop", "00000000", "testfile0"))
        firstfile = self.git.getfile(self.project_id, "test.file", "develop")
        self.assertTrue(self.git.updatefile(self.project_id, "test.file", "develop", "11111111", "testfile1"))
        secondfile = self.git.getfile(self.project_id, "test.file", "develop")
        self.assertNotEqual(firstfile["commit_id"], secondfile["commit_id"])
        self.assertNotEqual(firstfile["content"], secondfile["content"])
        self.assertTrue(self.git.deletefile(self.project_id, "test.file", "develop", "remove_testfile"))

    def test_search(self):
        self.assertGreater(len(self.git.searchproject(self.project['name'])), 0)
        assert isinstance(self.git.searchproject(self.project['name']), list)

    def test_filearchive(self):
        # test it works
        self.assertTrue(self.git.getfilearchive(self.project_id, self.project["name"] + ".tar.gz"))
        # test for failure
        self.failUnlessRaises(gitlab.exceptions.HttpError, self.git.getfilearchive, 999999)

    def test_group(self):
        for group in self.git.getgroups():
            self.git.deletegroup(group["id"])
        self.assertTrue(self.git.creategroup("test_group", "test_group"))
        assert isinstance(self.git.getgroups(), list)
        group = self.git.getgroups()[0]
        assert isinstance(self.git.listgroupmembers(group["id"]), list)
        self.assertEqual(len(self.git.listgroupmembers(group["id"])), 0)
        self.assertTrue(self.git.addgroupmember(group["id"], self.user_id, "master"))
        assert isinstance(self.git.listgroupmembers(group["id"]), list)
        self.assertGreater(len(self.git.listgroupmembers(group["id"])), 0)
        self.assertTrue(self.git.deletegroupmember(group["id"], self.user_id))
        self.assertFalse(self.git.addgroupmember(group["id"], self.user_id, "nonexistant"))
        self.assertTrue(self.git.deletegroup(group_id=group["id"]))

    def test_issues(self):
        issue = self.git.createissue(self.project_id, title="Test_issue", description="blaaaaa")
        assert isinstance(issue, dict)
        self.assertEqual(issue["title"], "Test_issue")
        issue = self.git.editissue(self.project_id, issue["id"], title="Changed")
        assert isinstance(issue, dict)
        self.assertEqual(issue["title"], "Changed")
        issue = self.git.editissue(self.project_id, issue["id"], state_event="close")
        self.assertEqual(issue["state"], "closed")
        self.assertGreater(len(self.git.getprojectissues(self.project_id)), 0)
        self.assertGreater(len(self.git.getissues()), 0)

    def test_system_hooks(self):
        # clean up before
        for hook in self.git.getsystemhooks():
            self.git.deletesystemhook(hook["id"])
        self.assertTrue(self.git.addsystemhook("http://github.com"))
        self.assertEqual(len(self.git.getsystemhooks()), 1)
        hook = self.git.getsystemhooks()[0]
        assert isinstance(self.git.testsystemhook(hook["id"]), list)
        self.assertTrue(self.git.deletesystemhook(hook["id"]))
        self.assertEqual(len(self.git.getsystemhooks()), 0)

    def test_milestones(self):
        milestone = self.git.createmilestone(self.project_id, title="test")
        assert isinstance(milestone, dict)
        self.assertGreater(len(self.git.getmilestones(self.project_id)), 0)
        assert isinstance(self.git.getmilestone(self.project_id, milestone["id"]), dict)
        self.assertEqual(milestone["title"], "test")
        milestone = self.git.editmilestone(self.project_id, milestone["id"], title="test2")
        self.assertEqual(milestone["title"], "test2")

    def test_merge(self):
        # TODO: check this and make this when I have internet so I can clone the test repo
        pass
        """
        # prepare for the merge
        print(self.git.listbranches(self.project_id))
        commit = self.git.listrepositorycommits(self.project_id)[5]
        branch = self.git.createbranch(self.project_id, "mergebranch", commit["id"])
        merge = self.git.createmergerequest(self.project_id, "master", "mergebranch", "testmerge")
        print(self.git.getmergerequests(self.project_id))
        print(self.git.getmergerequest(self.project_id, merge["id"]))
        print(self.git.getmergerequestcomments(self.project_id, merge["id"]))
        self.git.addcommenttomergerequest(self.project_id, merge["id"], "Hello")
        print(self.git.getmergerequestcomments(self.project_id, merge["id"]))
        self.git.updatemergerequest(self.project_id, merge["id"], title="testmerge2")
        print(self.git.getmergerequest(self.project_id, merge["id"]))
        self.git.acceptmergerequest(self.project_id, merge["id"], "closed!")
        print(self.git.getmergerequest(self.project_id, merge["id"]))
        """

    def test_notes(self):
        issue = self.git.createissue(self.project_id, title="test_issue")
        note = self.git.createissuewallnote(self.project_id, issue["id"], content="Test_note")
        assert isinstance(issue, dict)
        assert isinstance(note, dict)
        self.assertEqual(note["body"], "Test_note")
        assert isinstance(self.git.getissuewallnotes(self.project_id, issue["id"]), list)
        note2 = self.git.getissuewallnote(self.project_id, issue["id"], note["id"])
        assert isinstance(note2, dict)
        self.assertEqual(note, note2)

        snippet = self.git.createsnippet(self.project_id, "test_snippet", "test.py", "import this")
        note = self.git.createsnippetewallnote(self.project_id, snippet["id"], "test_snippet_content")
        assert isinstance(self.git.getsnippetwallnotes(self.project_id, snippet["id"]), list)
        note2 = self.git.getsnippetwallnote(self.project_id, snippet["id"], note["id"])
        assert isinstance(note2, dict)
        self.assertEqual(note, note2)

        # TODO: do first merge request so I can finish this one
        """
        self.git.getmergerequestwallnotes(self.project_id)
        self.git.getmergerequestwallnote(self.project_id)
        self.git.createmergerequestewallnote(self.project_id)
        """