# -*- coding: utf-8 -*-

import requests
import json
import markdown

# TODO: snippets
# TODO: repositories
# TODO: deploy keys
# TODo: notes


class Gitlab(object):
    def __init__(self, host, token=""):
        if token != "":
            self.token = token
            self.headers = {"PRIVATE-TOKEN": self.token}
        self.host = host
        self.projects_url = self.host + "/api/v3/projects"
        self.users_url = self.host + "/api/v3/users"
        self.keys_url = self.host + "/api/v3/user/keys"
        self.groups_url = self.host + "/api/v3/groups"

    def login(self, email, password):
        data = {"email": email, "password": password}
        r = requests.post(self.host + "/api/v3/session", data=data)
        if r.status_code == 201:
            self.token = json.loads(r.content)['private_token']
            self.headers = {"PRIVATE-TOKEN": self.token}
            return True
        else:
            print r
            return False

    def getUsers(self, id_=0):
        """
        Return a user list
        :param id_: the id of the user to get instead of getting all users, return all users if 0
        return: returs a dictionary of the users, false if there is an error
        """
        if id_ != 0:
            r = requests.get(self.host + "/api/v3/users/" + str(id_), headers=self.headers)
            user = json.loads(r.content)
            return [user['id'], user['username'], user['name'], user['email'], user['state'], user['created_at']]
        else:
            r = requests.get(self.users_url, headers=self.headers)
            if r.status_code == 200:
                return json.loads(r.content)
            else:
                return False

    def createUser(self, name, username, password, email, skype="", linkedin="", twitter="",
                   projects_limit="", extern_uid="", provider="", bio=""):
        """
        Create a user
        :param name: Obligatory
        :param username: Obligatory
        :param password: Obligatory
        :param email: Obligatory
        :return: TRue if the user was created, false if it wasn't (already exists)
        """
        data = {"name": name, "username": username, "password": password, "email": email, "skype": skype,
                "twitter": twitter, "linkedin": linkedin, "projects_limit": projects_limit, "extern_uid": extern_uid,
                "provider": provider, "bio": bio}
        r = requests.post(self.users_url, headers=self.headers, data=data)
        if r.status_code == 201:
            return True
        elif r.status_code == 404:
            print r
            return False

    def deleteUser(self, id_):
        """
        Deletes an user by ID
        :param id_: id of the user to delete
        :return: True if it deleted, False if it couldn't. False could happen for several reasons, but there isn't a
        good way of differenting them
        """
        r = requests.delete(self.users_url + "/" + str(id_), headers=self.headers)
        if r.status_code == 200:
            return True
        else:
            print r
            return False

    def currentUser(self):
        """
        Returns the current user parameters. The current user is linked to the secret token
        :return: a list with the current user properties
        """
        r = requests.get(self.host + "/api/v3/user", headers=self.headers)
        return json.loads(r.content)

    def editUser(self, id_, name="", username="", password="", email="", skype="", linkedin="", twitter="",
                 projects_limit="", extern_uid="", provider="", bio=""):
        data = {}
        if name != "":
            data["name"] = name
        if username != "":
            data["username"] = username
        if password != "":
            data["password"] = password
        if email != "":
            data["email"] = email
        if skype != "":
            data["skype"] = skype
        if linkedin != "":
            data["linkedin"] = linkedin
        if twitter != "":
            data["twitter"] = twitter
        if projects_limit != "":
            data["projects_limit"] = projects_limit
        if extern_uid != "":
            data["extern_uid"] = extern_uid
        if provider != "":
            data["provider"] = provider
        if bio != "":
            data["bio"] = bio
        r = requests.put(self.users_url + "/" + str(id_), headers=self.headers, data=data)
        if r.status_code == 404:
            return True
        # There is a problem here and that is that the api always return 404,
        #  doesn't matter what heappened with the request, so now way of knowing what happened
        else:
            return False

    def getSshKeys(self):
        """
        Gets all the ssh keys for the current user
        :return: a dictionary with the lists
        """
        r = requests.get(self.keys_url, headers=self.headers)
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            print r
            return False

    def getSshKey(self, id_):
        """
        Get a single ssh key identified by id_
        :param id_: the id of the key
        :return: the key itself
        """
        r = requests.get(self.keys_url + "/" + str(id_), headers=self.headers)
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            print r
            return False

    def addSshKey(self, title, key):
        """
        Add a new ssh key for the current user
        :param title: title of the new key
        :param key: the key itself
        :return: true if added, false if it didn't add it (it could be because the name or key already exists)
        """
        data = {"title": title, "key": key}
        r = requests.post(self.keys_url, headers=self.headers, data=data)
        if r.status_code == 201:
            return True
        else:
            print r
            return False

    def addSshKeyUser(self, id_, title, key):
        """
        Add a new ssh key for the user identified by id
        :param id_: id of the user to add the key to
        :param title: title of the new key
        :param key: the key itself
        :return: true if added, false if it didn't add it (it could be because the name or key already exists)
        """
        data = {"title": title, "key": key}
        r = requests.post(self.keys_url + "/" + str(id_) + "/keys", headers=self.headers, data=data)
        if r.status_code == 201:
            return True
        else:
            print r
            return False

    def deleteSshKey(self, id_):
        """
        Deletes an sshkey for the current user identified by id
        :param id_: the id of the key
        :return: False if it didn't delete it, True if it was deleted
        """
        r = requests.delete(self.keys_url + "/" + str(id_), headers=self.headers)
        if r.content == "null":  # always answer 200 so we need to examine the content
            print r
            return False
        else:
            return True

    def getProjects(self):
        """
        Returns a dictionary of all the projects
        :return: list with the repo name, description, last activity, web url, ssh url, owner and if its public
        """
        r = requests.get(self.projects_url, headers=self.headers)
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            print r
            return False

    def getProject(self, id_):
        """
        Get info for a project identified by id
        :param id_: id of the project
        :return: False if not found, a dictionary if found
        """
        r = requests.get(self.projects_url + "/" + str(id_), headers=self.headers)
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            print r
            return False

    def getProjectEvents(self, id_):
        """
        Get the project identified by id, events(commits)
        :param id_: id of the project
        :return: False if no project with that id, a dictionary with the events if found
        """
        r = requests.get(self.projects_url + "/" + str(id_) + "/events", headers=self.headers)
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            print r
            return False

    def createProject(self, name, description="", default_branch="", issues_enabled="", wall_enabled="",
                      merge_requests_enabled="", wiki_enabled="", snippets_enabled=""):
        """
        Create a project
        :param name: Obligatory
        :return: Dict of information on the newly created project if successful, False otherwise
        """
        data = {"name": name, "description": description, "default_branch": default_branch,
                "issues_enabled": issues_enabled, "wall_enabled": wall_enabled,
                "merge_requests_enabled": merge_requests_enabled, "wiki_enabled": wiki_enabled,
                "snippets_enabled": snippets_enabled}
        r = requests.post(self.projects_url, headers=self.headers, data=data)
        if r.status_code == 201:
            return json.loads(r.content)
        else:
            print r
            return False

    def createProjectUser(self, id_, name, description="", default_branch="", issues_enabled="", wall_enabled="",
                          merge_requests_enabled="", wiki_enabled="", snippets_enabled=""):
        """
        Create a project for the given user identified by id
        :param id_: id of the user to crete the project for
        :param name: Obligatory
        :return: True if it created the project, False otherwise
        """
        data = {"name": name, "description": description, "default_branch": default_branch,
                "issues_enabled": issues_enabled, "wall_enabled": wall_enabled,
                "merge_requests_enabled": merge_requests_enabled, "wiki_enabled": wiki_enabled,
                "snippets_enabled": snippets_enabled}
        r = requests.post(self.projects_url + "/user/" + str(id_), headers=self.headers, data=data)
        if r.status_code == 201:
            return True
        else:
            print r
            return False

    def listProjectMembers(self, id_):
        r = requests.get(self.projects_url + "/" + str(id_) + "/members", headers=self.headers)
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            print r
            return False

    def addProjectMember(self, id_, user_id, access_level):
        # check the access level and put into a number
        if access_level.lower() == "master":
            access_level = 40
        elif access_level.lower() == "developer":
            access_level = 30
        elif access_level.lower() == "reporter":
            access_level = 20
        else:
            access_level = 10
        data = {"id": id_, "user_id": user_id, "access_level": access_level}
        r = requests.post(self.projects_url + "/" + str(id_) + "/members", headers=self.headers, data=data)
        print r.status_code
        if r.status_code == 201:
            return True
        else:
            print r
            return False

    def editProjectMember(self,id_, user_id, access_level):
        if access_level.lower() == "master":
            access_level = 40
        elif access_level.lower() == "developer":
            access_level = 30
        elif access_level.lower() == "reporter":
            access_level = 20
        else:
            access_level = 10
        data = {"id": id_, "user_id": user_id, "access_level": access_level}
        r = requests.put(self.projects_url + "/" + str(id_) + "/members/" + str(user_id), headers=self.headers,
                         data=data)
        if r.status_code == 200:
            return True
        else:
            print r
            return False

    def deleteProjectMember(self, id_, user_id):
        r = requests.delete(self.projects_url + "/" + str(id_) + "/members/" + str(user_id), headers=self.headers)
        if r.status_code == 200:
            return True  # It always returns true, event if the member is not in the project

    def getProjectHooks(self, id_):
        r = requests.get(self.projects_url + "/" + str(id_) + "/hooks", headers=self.headers)
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            print r
            return False

    def getProjectHook(self, id_, hook_id):
        r = requests.get(self.projects_url + "/" + str(id_) + "/hooks/" + str(hook_id), headers=self.headers)
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            print r
            return False

    def addProjectHook(self, id_, url):
        data = {"id": id_, "url": url}
        r = requests.post(self.projects_url + "/" + str(id_) + "/hooks", headers=self.headers, data=data)
        print r.status_code
        if r.status_code == 201:
            return True
        else:
            print r
            return False

    def editProjectHook(self, id_, hook_id, url):
        data = {"id": id_, "hook_id": hook_id, "url": url}
        r = requests.put(self.projects_url + "/" + str(id_) + "/hooks/" + str(hook_id), headers=self.headers,
                         data=data)
        if r.status_code == 200:
            return True
        else:
            print r
            return False

    def deleteProjectHook(self, id_, hook_id):
        r = requests.delete(self.projects_url + "/" + str(id_) + "/hooks/" + str(hook_id), headers=self.headers)
        if r.status_code == 200:
            return True
        else:
            print r
            return False

    def listBranches(self, id_):
        r = requests.get(self.projects_url + "/" + str(id_) + "/repository/branches", headers=self.headers)
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            print r
            return False

    def listBranch(self, id_, branch):
        r = requests.get(self.projects_url + "/" + str(id_) + "/repository/branches/" + str(branch),
                         headers=self.headers)
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            print r
            return False

    def protectBranch(self, id_, branch):
        r = requests.put(self.projects_url + "/" + str(id_) + "/repository/branches/" + str(branch) + "/protect",
                         headers=self.headers)
        if r.status_code == 200:
            return True
        else:
            print r
            return False

    def unprotectBranch(self, id_, branch):
        r = requests.put(self.projects_url + "/" + str(id_) + "/repository/branches/" + str(branch) + "/unprotect",
                         headers=self.headers)
        if r.status_code == 200:
            return True
        else:
            print r
            return False

    def createForkRelation(self, id_, from_):
        data = {"id": id_, "forked_from_id": from_}
        r = requests.post(self.projects_url + "/" + str(id_) + "/fork/" + str(from_), headers=self.headers, data=data)
        if r.status_code == 201:
            return True
        else:
            print r
            return False

    def removeForkRelation(self, id_):
        r = requests.delete(self.projects_url + "/" + str(id_) + "/fork", headers=self.headers)
        if r.status_code == 200:
            return True
        else:
            print r
            return False

    def getIssues(self):
        r = requests.get(self.host + "/api/v3/issues", headers=self.headers)
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            print r
            return False

    def getProjectIssues(self, id_):
        r = requests.get(self.projects_url + "/" + str(id_) + "/issues", headers=self.headers)
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            print r
            return False

    def getProjectIssue(self, id_, issue_id):
        r = requests.get(self.projects_url + "/" + str(id_) + "/issues/" + str(issue_id), headers=self.headers)
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            print r
            return False

    def createIssue(self, id_, title, description="", assignee_id="", milestone_id="", labels=""):
        data = {"id": id, "title": title, "description": description, "assignee_id": assignee_id,
                "milestone_id": milestone_id, "labels": labels}
        r = requests.post(self.projects_url + "/" + str(id_) + "/issues", headers=self.headers, data=data)
        if r.status_code == 201:
            return True
        else:
            print r
            return False

    def editIssue(self, id_, issue_id, title="", description="", assignee_id="", milestone_id="", labels="",
                  state_event=""):
        data = {"id": id, "issue_id": issue_id, "title": title, "description": description, "assignee_id": assignee_id,
                "milestone_id": milestone_id, "labels": labels, "state_event": state_event}
        r = requests.put(self.projects_url + "/" + str(id_) + "/issues/" + str(issue_id), headers=self.headers,
                         data=data)
        if r.status_code == 201:
            return True
        else:
            print r
            return False

    def getMilestones(self, id_):
        r = requests.get(self.projects_url + "/" + str(id_) + "/milestones", headers=self.headers)
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            print r
            return False

    def getMilestone(self, id_, milestone_id):
        r = requests.get(self.projects_url + "/" + str(id_) + "/milestones/" + str(milestone_id), headers=self.headers)
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            print r
            return False

    def createMilestone(self, id_, title, description="", due_date=""):
        data = {"id": id_, "title": title, "description": description, "due_date": due_date}
        r = requests.post(self.projects_url + "/" + str(id_) + "/milestones", headers=self.headers, data=data)
        if r.status_code == 201:
            return True
        else:
            print r
            return False

    def editMilestone(self, id_, milestone_id, title="", description="", due_date="", state_event=""):
        data = {"id": id_, "milestone_id": milestone_id, "title": title, "description": description,
                "due_date": due_date, "state_event": state_event}
        r = requests.put(self.projects_url + "/" + str(id_) + "/milestones/" + str(milestone_id), headers=self.headers,
                         data=data)
        if r.status_code == 200:
            return True
        else:
            print r
            return False

    def listdeployKeys(self, id_):
        """
        Get a list of a project's deploy keys.
        :param id_: project id
        :return: the keys in a dictionary if success, false if not
        """
        r = requests.get(self.projects_url + "/" + str(id_) + "/keys", headers=self.headers)
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            print r
            return False

    def listDeployKey(self, id_, key_id):
        """
        Get a single key.
        :param id_: project id
        :param key_id: key id
        :return: the key in a dict if success, false if not
        """
        r = requests.get(self.projects_url + "/" + str(id_) + "/keys/" + str(key_id), headers=self.headers)
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            print r
            return False

    def addDeployKey(self, id_, title, key):
        """
        Creates a new deploy key for a project. If deploy key already exists in another project - it will be joined
        to project but only if original one was is accessible by same user
        :param id_: project id
        :param title: title of the key
        :param key: the key itself
        :return: true if sucess, false if not
        """
        data = {"id": id_, "title": title, "key": key}
        r = requests.post(self.projects_url + "/" + str(id_) + "/keys", headers=self.headers, data=data)
        if r.status_code == 201:
            return True
        else:
            print r
            return False

    def deleteDeployKey(self, id_, key_id):
        """
        Delete a deploy key from a project
        :param id_: project id
        :param key_id: key id to delete
        :return: true if success, false if not
        """
        r = requests.delete(self.projects_url + "/" + str(id_) + "/keys/" + str(key_id), headers=self.headers)
        if r.status_code == 200:
            return True
        else:
            print r
            return False

    def getReadme(self, repo, md=False):
        """
        returns the readme
        :param md: If false returns the raw readme, else returns the readme parsed by markdown
        :param repo: the web url to the project
        """
        r = requests.get(repo + "/raw/master/README.md?private_token=" + self.token)  # setting the headers doesn't work
        if "<!DOCTYPE html>" in r.content:  # having HTML in the response means we got a 404 from gitlab
            if md:
                return "<p>There isn't a README.md for that project</p>"
            else:
                return "There isn't a README.md for that project"
        else:
            if md:
                return markdown.markdown(r.content)
            else:
                return r.content

    def createGroup(self, name, path):
        """
        Creates a new group
        :param name: The name of the group
        :param path: The path for the group
        """
        r = requests.post(self.groups_url, data={'name': name, 'path': path}, headers=self.headers)
        if r.status_code == 201:
            return True
        else:
            print r
            return False

    def getGroups(self, id_=None):
        """
        Retrieve group information
        :param id_: Specify a group. Otherwise, all groups are returned
        """
        r = requests.get("{}/{}".format(self.groups_url, id_ if id_ else ""), headers=self.headers)
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            print r
            return False

    def moveProject(self, groupID, projectID):
        """
        Move a given project into a given group
        :param groupID: ID of the destination group
        :param projectID: ID of the project to be moved
        """
        r = requests.post("{}/{}/projects/{}".format(self.groups_url, groupID, projectID), headers=self.headers)
        if r.status_code == 201:
            return True
        else:
            print r
            return False