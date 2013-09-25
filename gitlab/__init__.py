# -*- coding: utf-8 -*-

import requests
import json
import markdown

# TODO: snippets
# TODO: repositories
# TODO: deploy keys
# TODo: notes


class Gitlab(object):
    def __init__(self, host, user, token=""):
        if token != "":
            self.token = token
            self.headers = {"PRIVATE-TOKEN": self.token}
        if host[-1] == '/':
            self.host = host[:-1]
        else:
            self.host = host
        self.projects_url = self.host + "/api/v3/projects"
        self.users_url = self.host + "/api/v3/users"
        self.keys_url = self.host + "/api/v3/user/keys"
        self.groups_url = self.host + "/api/v3/groups"
        self.user = user

    def login(self, user, password):
        self.user = user
        data = {"email": user, "password": password}
        request = requests.post(self.host + "/api/v3/session", data=data)
        if request.status_code == 201:
            self.token = json.loads(request.content)['private_token']
            self.headers = {"PRIVATE-TOKEN": self.token}
            return True
        else:
            print request
            return False

    def getUsers(self, id_=0, page=1, per_page=20, sudo=""):
        """
        Return a user list
        :param id_: the id of the user to get instead of getting all users,
         return all users if 0
        :param page: Which page to return (default is 1)
        :param per_page: Number of items to return per page (default is 20)
        :parm sudo: Username to execute the request under, defaults to the login user
        return: returs a dictionary of the users, false if there is an error
        """
        if sudo == "":
            sudo = self.user
        params = {'page': page, 'per_page': per_page, "sudo": sudo}
        if id_ != 0:
            request = requests.get(self.host + "/api/v3/users/" + str(id_),
                             params=params, headers=self.headers)
            user = json.loads(request.content)
            return [user['id'], user['username'], user['name'], user['email'],
                    user['state'], user['created_at']]
        else:
            request = requests.get(self.users_url, params=params, headers=self.headers)
            if request.status_code == 200:
                return json.loads(request.content)
            else:
                return False

    def createUser(self, name, username, password, email, skype="", linkedin="",
                   twitter="",
                   projects_limit="", extern_uid="", provider="", bio="", sudo=""):
        """
        Create a user
        :param name: Obligatory
        :param username: Obligatory
        :param password: Obligatory
        :param email: Obligatory
        :return: TRue if the user was created,false if it wasn't(already exists)
        """
        if sudo == "":
            sudo = self.user
        data = {"name": name, "username": username, "password": password,
                "email": email, "skype": skype,
                "twitter": twitter, "linkedin": linkedin,
                "projects_limit": projects_limit, "extern_uid": extern_uid,
                "provider": provider, "bio": bio, "sudo": sudo}
        request = requests.post(self.users_url, headers=self.headers, data=data)
        if request.status_code == 201:
            return True
        elif request.status_code == 404:
            print request
            return False

    def deleteUser(self, id_):
        """
        Deletes an user by ID
        :param id_: id of the user to delete
        :return: True if it deleted, False if it couldn't. False could happen
        for several reasons, but there isn't a
        good way of differenting them
        """
        request = requests.delete(self.users_url + "/" + str(id_),
                            headers=self.headers)
        if request.status_code == 200:
            return True
        else:
            print request
            return False

    def currentUser(self):
        """
        Returns the current user parameters. The current user is linked
        to the secret token
        :return: a list with the current user properties
        """
        request = requests.get(self.host + "/api/v3/user",
                         headers=self.headers)
        return json.loads(request.content)

    def editUser(self, id_, name="", username="", password="", email="",
                 skype="", linkedin="", twitter="",
                 projects_limit="", extern_uid="", provider="", bio="", sudo=""):
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
        if sudo == "":
            sudo = self.user
        data["sudo"] = self.user
        request = requests.put(self.users_url + "/" + str(id_),
                               headers=self.headers, data=data)
        if request.status_code == 404:
            return True
        # There is a problem here and that is that the api always return 404,
        #  doesn't matter what heappened with the request,
        # so now way of knowing what happened
        else:
            return False

    def getSshKeys(self):
        """
        Gets all the ssh keys for the current user
        :return: a dictionary with the lists
        """
        request = requests.get(self.keys_url, headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content)
        else:
            print request
            return False

    def getSshKey(self, id_):
        """
        Get a single ssh key identified by id_
        :param id_: the id of the key
        :return: the key itself
        """
        request = requests.get(self.keys_url + "/" + str(id_),
                               headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content)
        else:
            print request
            return False

    def addSshKey(self, title, key, sudo=""):
        """
        Add a new ssh key for the current user
        :param title: title of the new key
        :param key: the key itself
        :return: true if added, false if it didn't add it
        (it could be because the name or key already exists)
        """
        if sudo == "":
            sudo = self.user
        data = {"title": title, "key": key, "sudo": sudo}
        request = requests.post(self.keys_url, headers=self.headers, data=data)
        if request.status_code == 201:
            return True
        else:
            print request
            return False

    def addSshKeyUser(self, id_, title, key, sudo=""):
        """
        Add a new ssh key for the user identified by id
        :param id_: id of the user to add the key to
        :param title: title of the new key
        :param key: the key itself
        :return: true if added, false if it didn't add it
        (it could be because the name or key already exists)
        """
        if sudo == "":
            sudo = self.user
        data = {"title": title, "key": key, "sudo": sudo}
        request = requests.post(self.keys_url + "/" + str(id_) + "/keys",
                          headers=self.headers, data=data)
        if request.status_code == 201:
            return True
        else:
            print request
            return False

    def deleteSshKey(self, id_):
        """
        Deletes an sshkey for the current user identified by id
        :param id_: the id of the key
        :return: False if it didn't delete it, True if it was deleted
        """
        request = requests.delete(self.keys_url + "/" + str(id_),
                            headers=self.headers)
        if request.content == "null":
            print request
            return False
        else:
            return True

    def getProjects(self, page=1, per_page=20, sudo=""):
        """
        Returns a dictionary of all the projects
        :param page: Which page to return (default is 1)
        :param per_page: Number of items to return per page (default is 20)
        :return: list with the repo name, description, last activity,
         web url, ssh url, owner and if its public
        """
        if sudo == "":
            sudo = self.user
        params = {'page': page, 'per_page': per_page, 'sudo': sudo}
        request = requests.get(self.projects_url, params=params, headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content)
        else:
            print request
            return False

    def getProject(self, id_):
        """
        Get info for a project identified by id
        :param id_: id of the project
        :return: False if not found, a dictionary if found
        """
        request = requests.get(self.projects_url + "/" + str(id_),
                         headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content)
        else:
            print request
            return False

    def getProjectEvents(self, id_, page=1, per_page=20):
        """
        Get the project identified by id, events(commits)
        :param id_: id of the project
        :param page: Which page to return (default is 1)
        :param per_page: Number of items to return per page (default is 20)
        :return: False if no project with that id, a dictionary
         with the events if found
        """
        params = {'page': page, 'per_page': per_page}
        request = requests.get(self.projects_url + "/" + str(id_) +
                         "/events", params=params, headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content)
        else:
            print request
            return False

    def createProject(self, name, description="", default_branch="",
                      issues_enabled=0, wall_enabled=0,
                      merge_requests_enabled=0, wiki_enabled=0,
                      snippets_enabled=0, public=0, sudo=""):
        """
        Create a project
        :param name: Obligatory
        :return: Dict of information on the newly created project if successful,
         False otherwise
        """
        if sudo == "":
            sudo = self.user
        data = {"name": name, "description": description,
                "default_branch": default_branch,
                "issues_enabled": issues_enabled, "wall_enabled": wall_enabled,
                "merge_requests_enabled": merge_requests_enabled,
                "wiki_enabled": wiki_enabled,
                "snippets_enabled": snippets_enabled, "sudo": sudo}

        # if gitlab is the new 6th version, there is a public option for the
        # project creation
        if public != 0:
            data['public'] = public
        #request now works with both GitLab 5 and GitLab 6.
        request = requests.post(self.projects_url, headers=self.headers,
                                data=data)
        if request.status_code == 201:
            return json.loads(request.content)
        else:
            print request
            return False

    def createProjectUser(self, id_, name, description="", default_branch="",
                          issues_enabled=0, wall_enabled=0,
                          merge_requests_enabled=0, wiki_enabled=0,
                          snippets_enabled=0, sudo=""):
        """
        Create a project for the given user identified by id
        :param id_: id of the user to crete the project for
        :param name: Obligatory
        :return: True if it created the project, False otherwise
        """
        if sudo == "":
            sudo = self.user
        data = {"name": name, "description": description,
                "default_branch": default_branch,
                "issues_enabled": issues_enabled, "wall_enabled": wall_enabled,
                "merge_requests_enabled": merge_requests_enabled,
                "wiki_enabled": wiki_enabled,
                "snippets_enabled": snippets_enabled, "sudo": sudo}
        request = requests.post(self.projects_url + "/user/" + str(id_),
                          headers=self.headers, data=data)
        if request.status_code == 201:
            return True
        else:
            print request
            return False

    def listProjectMembers(self, id_):
        request = requests.get(self.projects_url + "/" + str(id_) + "/members",
                         headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content)
        else:
            print request
            return False

    def addProjectMember(self, id_, user_id, access_level, sudo=""):
        # check the access level and put into a number
        if sudo == "":
            sudo = self.user
        if access_level.lower() == "master":
            access_level = 40
        elif access_level.lower() == "developer":
            access_level = 30
        elif access_level.lower() == "reporter":
            access_level = 20
        else:
            access_level = 10
        data = {"id": id_, "user_id": user_id, "access_level": access_level}
        request = requests.post(self.projects_url + "/" + str(id_) + "/members",
                          headers=self.headers, data=data)
        if request.status_code == 201:
            return True
        else:
            print request
            return False

    def editProjectMember(self, id_, user_id, access_level, sudo=""):
        if sudo == "":
            sudo = self.user
        if access_level.lower() == "master":
            access_level = 40
        elif access_level.lower() == "developer":
            access_level = 30
        elif access_level.lower() == "reporter":
            access_level = 20
        else:
            access_level = 10
        data = {"id": id_, "user_id": user_id, "access_level": access_level, "sudo": sudo}
        request = requests.put(self.projects_url + "/" + str(id_) + "/members/"
                               + str(user_id), headers=self.headers, data=data)
        if request.status_code == 200:
            return True
        else:
            print request
            return False

    def deleteProjectMember(self, id_, user_id):
        request = requests.delete(self.projects_url + "/" + str(id_)
                                  + "/members/" + str(user_id),
                                  headers=self.headers)
        if request.status_code == 200:
            return True  # It always returns true

    def getProjectHooks(self, id_):
        request = requests.get(self.projects_url + "/" + str(id_) + "/hooks",
                         headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content)
        else:
            print request
            return False

    def getProjectHook(self, id_, hook_id):
        request = requests.get(self.projects_url + "/" + str(id_) + "/hooks/" +
                         str(hook_id), headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content)
        else:
            print request
            return False

    def addProjectHook(self, id_, url):
        data = {"id": id_, "url": url}
        request = requests.post(self.projects_url + "/" + str(id_) + "/hooks",
                          headers=self.headers, data=data)
        if request.status_code == 201:
            return True
        else:
            print request
            return False

    def editProjectHook(self, id_, hook_id, url, sudo=""):
        if sudo == "":
            sudo = self.user
        data = {"id": id_, "hook_id": hook_id, "url": url, "sudo": sudo}
        request = requests.put(self.projects_url + "/" + str(id_) + "/hooks/" +
                         str(hook_id), headers=self.headers,
                         data=data)
        if request.status_code == 200:
            return True
        else:
            print request
            return False

    def deleteProjectHook(self, id_, hook_id):
        request = requests.delete(self.projects_url + "/" + str(id_)
                                  + "/hooks/"
                                  + str(hook_id), headers=self.headers)
        if request.status_code == 200:
            return True
        else:
            print request
            return False

    def listBranches(self, id_):
        request = requests.get(self.projects_url + "/" + str(id_) +
                         "/repository/branches", headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content)
        else:
            print request
            return False

    def listBranch(self, id_, branch):
        request = requests.get(self.projects_url + "/" + str(id_) +
                         "/repository/branches/" + str(branch),
                         headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content)
        else:
            print request
            return False

    def protectBranch(self, id_, branch):
        request = requests.put(self.projects_url + "/" + str(id_) +
                         "/repository/branches/" + str(branch) + "/protect",
                         headers=self.headers)
        if request.status_code == 200:
            return True
        else:
            print request
            return False

    def unprotectBranch(self, id_, branch):
        request = requests.put(self.projects_url + "/" + str(id_) +
                         "/repository/branches/" + str(branch) + "/unprotect",
                         headers=self.headers)
        if request.status_code == 200:
            return True
        else:
            print request
            return False

    def createForkRelation(self, id_, from_):
        data = {"id": id_, "forked_from_id": from_}
        request = requests.post(self.projects_url + "/" + str(id_) +
                          "/fork/" + str(from_), headers=self.headers,
                          data=data)
        if request.status_code == 201:
            return True
        else:
            print request
            return False

    def removeForkRelation(self, id_):
        request = requests.delete(self.projects_url + "/" + str(id_) +
                            "/fork", headers=self.headers)
        if request.status_code == 200:
            return True
        else:
            print request
            return False

    def getIssues(self, page=1, per_page=20, sudo=""):
        """
        Return a global list of issues for your user.
        :param page: Which page to return (default is 1)
        :param per_page: Number of items to return per page (default is 20)
        """
        if sudo == "":
            sudo = self.user
        params = {'page': page, 'per_page': per_page, "sudo": sudo}
        request = requests.get(self.host + "/api/v3/issues",
                               params=params, headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content)
        else:
            print request
            return False

    def getProjectIssues(self, id_, page=1, per_page=20, sudo=""):
        """
        Return a list of issues for project id_.
        :param id_: The id for the project.
        :param page: Which page to return (default is 1)
        :param per_page: Number of items to return per page (default is 20)
        """
        if sudo == "":
            sudo = self.user
        params = {'page': page, 'per_page': per_page, "sudo": sudo}
        request = requests.get(self.projects_url + "/" + str(id_) +
                         "/issues", params=params, headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content)
        else:
            print request
            return False

    def getProjectIssue(self, id_, issue_id):
        request = requests.get(self.projects_url + "/" + str(id_) +
                         "/issues/" + str(issue_id), headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content)
        else:
            print request
            return False

    def createIssue(self, id_, title, description="", assignee_id="",
                    milestone_id="", labels="", sudo=""):
        if sudo == "":
            sudo = self.user
        data = {"id": id, "title": title, "description": description,
                "assignee_id": assignee_id,
                "milestone_id": milestone_id, "labels": labels, "sudo": sudo}
        request = requests.post(self.projects_url + "/" + str(id_) + "/issues",
                          headers=self.headers, data=data)
        if request.status_code == 201:
            return True
        else:
            print request
            return False

    def editIssue(self, id_, issue_id, title="", description="",
                  assignee_id="", milestone_id="", labels="",
                  state_event="", sudo=""):
        if sudo == "":
            sudo = self.user
        data = {"id": id, "issue_id": issue_id, "title": title,
                "description": description, "assignee_id": assignee_id,
                "milestone_id": milestone_id, "labels": labels,
                "state_event": state_event, "sudo": sudo}
        request = requests.put(self.projects_url + "/" + str(id_) + "/issues/" +
                         str(issue_id), headers=self.headers,
                         data=data)
        if request.status_code == 201:
            return True
        else:
            print request
            return False

    def getMilestones(self, id_):
        request = requests.get(self.projects_url + "/" + str(id_) +
                         "/milestones", headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content)
        else:
            print request
            return False

    def getMilestone(self, id_, milestone_id):
        request = requests.get(self.projects_url + "/" + str(id_)
                               + "/milestones/"
                               + str(milestone_id), headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content)
        else:
            print request
            return False

    def createMilestone(self, id_, title, description="", due_date="", sudo=""):
        if sudo == "":
            sudo = self.user
        data = {"id": id_, "title": title, "description": description,
                "due_date": due_date, "sudo": sudo}
        request = requests.post(self.projects_url + "/" + str(id_) +
                          "/milestones", headers=self.headers, data=data)
        if request.status_code == 201:
            return True
        else:
            print request
            return False

    def editMilestone(self, id_, milestone_id, title="", description="",
                      due_date="", state_event="", sudo=""):
        if sudo == "":
            sudo = self.user
        data = {"id": id_, "milestone_id": milestone_id, "title": title,
                "description": description,
                "due_date": due_date, "state_event": state_event, "sudo": sudo}
        request = requests.put(self.projects_url + "/" + str(id_)
                               + "/milestones/"
                               + str(milestone_id), headers=self.headers,
                         data=data)
        if request.status_code == 200:
            return True
        else:
            print request
            return False

    def listdeployKeys(self, id_):
        """
        Get a list of a project's deploy keys.
        :param id_: project id
        :return: the keys in a dictionary if success, false if not
        """
        request = requests.get(self.projects_url + "/" + str(id_) + "/keys",
                         headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content)
        else:
            print request
            return False

    def listDeployKey(self, id_, key_id):
        """
        Get a single key.
        :param id_: project id
        :param key_id: key id
        :return: the key in a dict if success, false if not
        """
        request = requests.get(self.projects_url + "/" + str(id_) + "/keys/" +
                         str(key_id), headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content)
        else:
            print request
            return False

    def addDeployKey(self, id_, title, key, sudo=""):
        """
        Creates a new deploy key for a project.
        If deploy key already exists in another project - it will be joined
        to project but only if original one was is accessible by same user
        :param id_: project id
        :param title: title of the key
        :param key: the key itself
        :return: true if sucess, false if not
        """
        if sudo == "":
            sudo = self.user
        data = {"id": id_, "title": title, "key": key, "sudo": sudo}
        request = requests.post(self.projects_url + "/" + str(id_) + "/keys",
                          headers=self.headers, data=data)
        if request.status_code == 201:
            return True
        else:
            print request
            return False

    def deleteDeployKey(self, id_, key_id):
        """
        Delete a deploy key from a project
        :param id_: project id
        :param key_id: key id to delete
        :return: true if success, false if not
        """
        request = requests.delete(self.projects_url + "/" + str(id_) + "/keys/"
                                  + str(key_id), headers=self.headers)
        if request.status_code == 200:
            return True
        else:
            print request
            return False

    def getReadme(self, repo, md=False):
        """
        returns the readme
        :param md: If false returns the raw readme,
        else returns the readme parsed by markdown
        :param repo: the web url to the project
        """
        request = requests.get(repo + "/raw/master/README.md?private_token=" +
                         self.token)  # setting the headers doesn't work
        if "<!DOCTYPE html>" in request.content:  # having HTML means a 404
            if md:
                return "<p>There isn't a README.md for that project</p>"
            else:
                return "There isn't a README.md for that project"
        else:
            if md:
                return markdown.markdown(request.content)
            else:
                return request.content

    def createGroup(self, name, path):
        """
        Creates a new group
        :param name: The name of the group
        :param path: The path for the group
        """
        request = requests.post(self.groups_url,
                                data={'name': name, 'path': path},
                                headers=self.headers)
        if request.status_code == 201:
            return True
        else:
            print request
            return False

    def getGroups(self, id_=None, page=1, per_page=20, sudo=""):
        """
        Retrieve group information
        :param id_: Specify a group. Otherwise, all groups are returned
        :param page: Which page to return (default is 1)
        :param per_page: Number of items to return per page (default is 20)
        """
        if sudo == "":
            sudo = self.user
        params = {'page': page, 'per_page': per_page, "sudo": sudo}
        request = requests.get("{0}/{1}".format(self.groups_url,
                                                id_ if id_ else ""),
                               params=params, headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content)
        else:
            print request
            return False

    def moveProject(self, groupID, projectID):
        """
        Move a given project into a given group
        :param groupID: ID of the destination group
        :param projectID: ID of the project to be moved
        """
        request = requests.post("{0}/{1}/projects/{2}".format(self.groups_url,
                                                        groupID, projectID),
                          headers=self.headers)
        if request.status_code == 201:
            return True
        else:
            print request
            return False

    def getMergeRequests(self, projectID, page=None, per_page=None, sudo=""):
        """
        Get all the merge requests for a project.
        :param projectID: ID of the project to retrieve merge requests for
        :param page: If pagination is set, which page to return
        :param per_page: Number of merge requests to return per page
        """
        if sudo == "":
            sudo = self.user
        params = {'page': page, 'per_page': per_page, "sudo": sudo}
        url_str = '{0}/{1}/merge_requests'.format(self.projects_url, projectID)
        request = requests.get(url_str, params=params, headers=self.headers)

        if request.status_code == 200:
            return json.loads(request.content)
        else:
            print request
            return False

    def getMergeRequest(self, projectID, mergeRequestID):
        """
        Get information about a specific merge request.
        :param projectID: ID of the project
        :param mergeRequestID: ID of the merge request
        """
        url_str = '{0}/{1}/merge_request/{2}'.format(self.projects_url,
                                                     projectID, mergeRequestID)
        request = requests.get(url_str, headers=self.headers)

        if request.status_code == 200:
            return json.loads(request.content)
        else:
            print request
            return False
            
    def createMergeRequest(self, projectID, sourceBranch, targetBranch,
                           title, assigneeID=None, sudo=""):
        """
        Create a new merge request.
        :param projectID: ID of the project originating the merge request
        :param sourceBranch: name of the branch to merge from
        :param targetBranch: name of the branch to merge to
        :param title: Title of the merge request
        :param assigneeID: Assignee user ID
        """
        if sudo == "":
            sudo = self.user
        url_str = '{0}/{1}/merge_requests'.format(self.projects_url, projectID)
        params = {'source_branch': sourceBranch,
                  'target_branch': targetBranch,
                  'title': title,
                  'assignee_id': assigneeID, "sudo": sudo}

        request = requests.post(url_str, data=params, headers=self.headers)
        if request.status_code == 201:
            return True
        else:
            print request
            return False

    def updateMergeRequest(self, projectID, mergeRequestID, sourceBranch=None,
                           targetBranch=None, title=None,
                           assigneeID=None, closed=None, sudo=""):
        """
        Update an existing merge request.
        :param projectID: ID of the project originating the merge request
        :param mergeRequestID: ID of the merge request to update
        :param sourceBranch: name of the branch to merge from
        :param targetBranch: name of the branch to merge to
        :param title: Title of the merge request
        :param assigneeID: Assignee user ID
        :param closed: MR status.  True = closed
        """
        if sudo == "":
            sudo = self.user
        url_str = '{0}/{1}/merge_request/{2}'.format(self.projects_url,
                                                     projectID, mergeRequestID)
        params = {'source_branch': sourceBranch,
                  'target_branch': targetBranch,
                  'title': title,
                  'assignee_id': assigneeID,
                  'closed': closed,
                  'sudo': sudo}

        request = requests.post(url_str, data=params, headers=self.headers)
        if request.status_code == 201:
            return True
        else:
            print request
            return False

    def addCommentToMergeRequest(self, projectID, mergeRequestID, note):
        """
        Add a comment to a merge request.
        :param projectID: ID of the project originating the merge request
        :param mergeRequestID: ID of the merge request to comment on
        :param note: Text of comment
        """
        url_str = '{0}/{1}/merge_request/{2}/comments'.format(self.projects_url,
                                                              projectID,
                                                              mergeRequestID)
        request = requests.post(url_str, data={'note': note},
                                headers=self.headers)

        if request.status_code == 201:
            return True
        else:
            print request
            return False
