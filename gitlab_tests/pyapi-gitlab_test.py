"""
pyapi-gitlab tests
"""

import unittest2 as unittest
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
password = os.environ.get('gitlab_password', '5iveL!fe')
host = os.environ.get('gitlab_host', 'http://192.168.1.100')


class GitlabTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.git = gitlab.Gitlab(host=host)
        cls.git.login(user=user, password=password)
        name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        cls.project = cls.git.createproject(name=name, visibility_level="private",
                                            import_url="https://github.com/Itxaka/pyapi-gitlab.git")
        # wait a bit for the project to be fully imported
        time.sleep(20)
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
        assert isinstance(self.git.getproject(self.project['path_with_namespace']), dict)
        self.assertFalse(self.git.getproject("wrong"))

        # test getprojectsall
        assert isinstance(self.git.getprojectsall(), list)
        assert isinstance(self.git.getprojectsall(page=5), list)
        assert isinstance(self.git.getprojectsall(per_page=7), list)

        # test getownprojects
        assert isinstance(self.git.getprojectsowned(), list)
        assert isinstance(self.git.getprojectsowned(page=5), list)
        assert isinstance(self.git.getprojectsowned(per_page=7), list)

        # test events
        assert isinstance(self.git.getprojectevents(self.project_id), list)
        assert isinstance(self.git.getprojectevents(self.project_id, page=3), list)
        assert isinstance(self.git.getprojectevents(self.project_id, per_page=4), list)

        # add-remove project members
        self.assertTrue(self.git.addprojectmember(self.project_id, user_id=self.user_id, access_level="reporter"))
        assert isinstance(self.git.getprojectmembers(self.project_id), list)
        self.assertTrue(self.git.editprojectmember(self.project_id, user_id=self.user_id, access_level="master"))
        self.assertTrue(self.git.deleteprojectmember(self.project_id, user_id=1))

        # Hooks testing
        assert isinstance(self.git.addprojecthook(self.project_id, "http://web.com"), dict)
        assert isinstance(self.git.getprojecthooks(self.project_id), list)
        assert isinstance(self.git.getprojecthook(self.project_id,
                                                  self.git.getprojecthooks(self.project_id)[0]['id']), dict)
        self.assertTrue(self.git.editprojecthook(self.project_id,
                                                 self.git.getprojecthooks(self.project_id)[0]['id'], "http://another.com"))
        self.assertTrue(self.git.deleteprojecthook(self.project_id,
                                                   self.git.getprojecthooks(self.project_id)[0]['id']))

        # Forks testing
        name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        newproject = self.git.createproject(name)
        # set it as forker from the main project
        self.git.createforkrelation(newproject["id"], self.project_id)
        newproject = self.git.getproject(newproject["id"])
        self.assertIn("forked_from_project", newproject)

        # remove the fork relation
        self.assertTrue(self.git.removeforkrelation(newproject["id"]))
        newproject = self.git.getproject(newproject["id"])
        with self.assertRaises(KeyError) as raises:
            _ = newproject["forked_from_project"]

        # test moveproject
        for group in self.git.getgroups():
            self.git.deletegroup(group["id"])
        group = self.git.creategroup("movegroup", "movegroup")
        assert isinstance(group, dict)
        assert isinstance(self.git.moveproject(group["id"], newproject["id"]), dict)
        project = self.git.getproject(newproject["id"])
        self.assertEqual("movegroup", project["namespace"]["name"])

        # Clean up the newgroup
        self.git.deleteproject(newproject["id"])

        # Create an actual fork of the main project
        self.git.createfork(self.project_id)

    def test_deploykeys(self):
        keys = self.git.getdeploykeys(self.project_id)
        assert isinstance(keys, list)
        self.assertEqual(len(keys), 0)
        if ssh_test:
            name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            rsa_key = RSA.generate(1024)
            assert isinstance(self.git.adddeploykey(project_id=self.project_id, title=name,
                                                    key=str(rsa_key.publickey().exportKey(format="OpenSSH"))), dict)
            keys = self.git.getdeploykeys(self.project_id)
            self.assertGreater(len(keys), 0)
            key = keys[0]
            assert isinstance(self.git.getdeploykey(self.project_id, key["id"]), dict)
            self.assertTrue(self.git.deletedeploykey(self.project_id, key["id"]))
            keys = self.git.getdeploykeys(self.project_id)
            self.assertEqual(len(keys), 0)

    def test_branch(self):
        sha1 = self.git.getrepositorycommits(project_id=self.project_id)[0]["id"]
        assert isinstance(self.git.createbranch(self.project_id, branch="deleteme", ref=sha1), dict)
        self.assertTrue(self.git.deletebranch(self.project_id, branch="deleteme"))
        assert isinstance(self.git.getbranches(self.project_id), list)
        assert isinstance(self.git.getbranch(self.project_id, branch="develop"), dict)
        self.assertTrue(self.git.protectbranch(self.project_id, branch="develop"))
        self.assertTrue(self.git.unprotectbranch(self.project_id, branch="develop"))

    def test_sshkeys(self):
        assert isinstance(self.git.getsshkeys(), list)
        self.assertEquals(len(self.git.getsshkeys()), 0)
        # not working due a bug? in pycrypto: https://github.com/dlitz/pycrypto/issues/99

        if ssh_test:
            name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            rsa_key = RSA.generate(1024)
            self.assertTrue(self.git.addsshkey(title=name, key=str(rsa_key.publickey().exportKey(format="OpenSSH"))))
            self.assertGreater(self.git.getsshkeys(), 0)
            keys = self.git.getsshkeys()
            assert isinstance(keys, list)
            key = self.git.getsshkeys()[0]
            assert isinstance(key, dict)
            self.assertTrue(self.git.deletesshkey(key["id"]))

            name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            rsa_key = RSA.generate(1024)
            self.assertTrue(self.git.addsshkeyuser(self.user_id, title=name,
                                                   key=str(rsa_key.publickey().exportKey(format="OpenSSH"))))
            self.assertGreater(self.git.getsshkeys(), 0)
            keys = self.git.getsshkeys()
            assert isinstance(keys, list)
            key = self.git.getsshkeys()[0]
            assert isinstance(key, dict)
            self.assertTrue(self.git.deletesshkey(key["id"]))

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
        assert isinstance(self.git.getrepositorycommits(self.project_id), list)
        assert isinstance(self.git.getrepositorycommits(self.project_id, page=1), list)
        assert isinstance(self.git.getrepositorycommits(self.project_id, per_page=7), list)
        commit = self.git.getrepositorycommits(self.project_id)[0]

        # tags
        tags = self.git.getrepositorytags(self.project_id)
        assert isinstance(tags, list)
        tag = self.git.createrepositorytag(self.project_id, "test_tag", commit["id"], "test_tag_message")
        assert isinstance(tag, dict)
        self.assertEqual(tag["name"], "test_tag")

        assert isinstance(self.git.getrepositorycommit(self.project_id, commit["id"]), dict)
        assert isinstance(self.git.getrepositorycommitdiff(self.project_id, commit["id"]), list)
        assert isinstance(self.git.getrepositorytree(self.project_id), list)
        assert isinstance(self.git.getrepositorytree(self.project_id, path="docs"), list)
        assert isinstance(self.git.getrepositorytree(self.project_id, ref_name="develop"), list)
        assert isinstance(str(self.git.getrawblob(self.project_id, commit['id'])), str)
        assert isinstance(str(self.git.getrawfile(self.project_id, commit['id'], "setup.py")), str)
        commit = self.git.getrepositorycommits(self.project_id)
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
        assert self.git.getcontributors(self.project_id) is not False

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
        assert isinstance(self.git.creategroup("test_group", "test_group"), dict)
        assert isinstance(self.git.getgroups(), list)
        group = self.git.getgroups()[0]
        assert isinstance(self.git.getgroupmembers(group["id"]), list)
        try:
            # Gitlab < 7.8
            self.assertEqual(len(self.git.getgroupmembers(group["id"])), 0)
            self.assertTrue(self.git.addgroupmember(group["id"], self.user_id, "master"))
        except AssertionError:
            # In Gitlab > 7.7, Admin is automatically added to all groups. Keep breaking that api champs.
            self.assertEqual(len(self.git.getgroupmembers(group["id"])), 1)
        assert isinstance(self.git.getgroupmembers(group["id"]), list)
        self.assertGreater(len(self.git.getgroupmembers(group["id"])), 0)
        self.assertTrue(self.git.deletegroupmember(group["id"], self.user_id))
        self.assertFalse(self.git.addgroupmember(group["id"], self.user_id, "nonexistant"))
        self.assertTrue(self.git.deletegroup(group_id=group["id"]))

        self.git.creategroup("not_the_group", "not_the_group")
        not_the_group = self.git.getgroups(search="not_the_group")[0]
        self.assertNotEqual(not_the_group["id"], group["id"])
        self.assertEqual(not_the_group["name"], "not_the_group")

    def test_namespaces(self):
        assert isinstance(self.git.getnamespaces(), list)
        group = self.git.getgroups()[0]
        self.assertGreaterEqual(len(self.git.getnamespaces(search=group["name"])), 1)

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
        assert isinstance(self.git.getprojectissue(self.project_id, issue["id"]), dict)
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
        # prepare for the merge
        commit = self.git.getrepositorycommits(self.project_id)[5]
        branch = self.git.createbranch(self.project_id, "mergebranch", commit["id"])
        merge = self.git.createmergerequest(self.project_id, "develop", "mergebranch", "testmerge")

        assert isinstance(self.git.getmergerequests(self.project_id), list)
        merge_request = self.git.getmergerequest(self.project_id, merge["id"])
        assert isinstance(merge_request, dict)
        self.assertEqual(merge_request["title"], "testmerge")

        self.assertEqual(len(self.git.getmergerequestcomments(self.project_id, merge["id"])), 0)
        self.assertTrue(self.git.addcommenttomergerequest(self.project_id, merge["id"], "Hello"))
        comments = self.git.getmergerequestcomments(self.project_id, merge["id"])
        self.assertEqual(comments[0]["note"], "Hello")

        self.assertTrue(self.git.updatemergerequest(self.project_id, merge["id"], title="testmerge2"))
        merge_request = self.git.getmergerequest(self.project_id, merge["id"])
        self.assertEqual(merge_request["title"], "testmerge2")
        self.assertEqual(self.git.getmergerequest(self.project_id, merge["id"])["state"], "opened")
        self.assertTrue(self.git.acceptmergerequest(self.project_id, merge["id"], "closed!"))
        self.assertEqual(self.git.getmergerequest(self.project_id, merge["id"])["state"], "merged")

    def test_commit_comment(self):
        commit = self.git.getrepositorycommits(self.project_id)[5]
        branch = self.git.createbranch(self.project_id, "mergebranch", commit["id"])
        merge = self.git.createmergerequest(self.project_id, "develop", "mergebranch", "testmerge")

        self.assertTrue(self.git.addcommenttocommit(self.project_id, merge['author'], merge['source_branch'], 'README.md', 1, 'Hello'))


    def test_notes(self):

        # issue wallnotes
        issue = self.git.createissue(self.project_id, title="test_issue")
        note = self.git.createissuewallnote(self.project_id, issue["id"], content="Test_note")
        assert isinstance(issue, dict)
        assert isinstance(note, dict)
        self.assertEqual(note["body"], "Test_note")
        assert isinstance(self.git.getissuewallnotes(self.project_id, issue["id"]), list)
        note2 = self.git.getissuewallnote(self.project_id, issue["id"], note["id"])
        assert isinstance(note2, dict)
        self.assertEqual(note["body"], note2["body"])

        # snippet wallnotes
        snippet = self.git.createsnippet(self.project_id, "test_snippet", "test.py", "import this")
        note = self.git.createsnippetewallnote(self.project_id, snippet["id"], "test_snippet_content")
        assert isinstance(self.git.getsnippetwallnotes(self.project_id, snippet["id"]), list)
        note2 = self.git.getsnippetwallnote(self.project_id, snippet["id"], note["id"])
        assert isinstance(note2, dict)
        self.assertEqual(note["body"], note2["body"])

        # merge request wallnotes
        commit = self.git.getrepositorycommits(self.project_id)[5]
        branch = self.git.createbranch(self.project_id, "notesbranch", commit["id"])
        merge = self.git.createmergerequest(self.project_id, "develop", "notesbranch", "testnotes")
        self.assertEqual(len(self.git.getmergerequestwallnotes(self.project_id, merge["id"])), 0)
        note = self.git.createmergerequestewallnote(self.project_id, merge["id"], "test_content")
        assert isinstance(note, dict)
        note2 = self.git.getmergerequestwallnote(self.project_id, merge["id"], note["id"])
        assert isinstance(note2, dict)
        self.assertEqual(note["body"], note2["body"])
        self.assertEqual(len(self.git.getmergerequestwallnotes(self.project_id, merge["id"])), 1)

    def test_labels(self):
        labels = self.git.getlabels(self.project_id)
        assert isinstance(labels, list)
        self.assertEqual(len(labels), 0)
        assert self.git.createlabel(self.project_id, "test_label", "#FFAABB") is not False
        labels = self.git.getlabels(self.project_id)
        self.assertEqual(len(labels), 1)
        self.assertTrue(self.git.deletelabel(self.project_id, "test_label"))
        labels = self.git.getlabels(self.project_id)
        self.assertEqual(len(labels), 0)

    def test_sudo(self):
        name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        newuser = self.git.createuser(name, name, "sudo_user", "{}@user.org".format(name))
        # change to the new user
        self.git.setsudo(user=newuser["id"])
        self.assertEqual(len(self.git.getprojects()), 0)
        self.assertEqual(self.git.currentuser()["username"], name)
        # change back to logged user
        self.git.setsudo()
        self.assertGreaterEqual(len(self.git.getprojects()), 1)
        self.assertEqual(self.git.currentuser()["username"], "root")
        self.git.deleteuser(newuser["id"])
