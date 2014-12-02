# -*- coding: utf-8 -*-
"""
pyapi-gitlab, a gitlab python wrapper for the gitlab API
by Itxaka Serrano Garcia <itxakaserrano@gmail.com>
"""

import requests
import json
try:
    import markdown
except ImportError:
    pass
from . import exceptions


class Gitlab(object):
    """
    Gitlab class
    """
    def __init__(self, host, token="", verify_ssl=True):
        """
        on init we setup the token used for all the api calls and all the urls
        :param host: host of gitlab
        :param token: token
        """
        if token != "":
            self.token = token
            self.headers = {"PRIVATE-TOKEN": self.token}
        if not host:
            raise ValueError("host argument may not be empty")
        if host[-1] == '/':
            self.host = host[:-1]
        else:
            self.host = host
        if self.host[:7] == 'http://' or self.host[:8] == 'https://':
            pass
        else:
            self.host = 'https://' + self.host

        self.api_url = self.host + "/api/v3"
        self.projects_url = self.api_url + "/projects"
        self.users_url = self.api_url + "/users"
        self.keys_url = self.api_url + "/user/keys"
        self.groups_url = self.api_url + "/groups"
        self.search_url = self.api_url + "/projects/search/"
        self.hook_url = self.api_url + "/hooks"
        self.verify_ssl = verify_ssl

    def login(self, email=None, password=None, user=None):
        """
        Logs the user in and setups the header with the private token
        :param user: gitlab user
        :param password: gitlab password
        :return: True if login successfull
        """
        if user != None:
            data = {"login": user, "password": password}
        elif email != None:
            data = {"email": email, "password": password}
        else:
            raise ValueError('Neither username nor email provided to login')

        request = requests.post(self.host + "/api/v3/session", data=data, 
                                verify=self.verify_ssl,
                                headers={"connection": "close"})
        if request.status_code == 201:
            self.token = json.loads(request.content.decode("utf-8"))['private_token']
            self.headers = {"PRIVATE-TOKEN": self.token,
                            "connection": "close"}
            return True
        else:
            msg = json.loads(request.content.decode("utf-8"))['message']
            raise exceptions.HttpError(msg)

    def getusers(self, search=None, page=1, per_page=20):
        """
        Return a user list
        :param search: Optional search query
        :param page: Which page to return (default is 1)
        :param per_page: Number of items to return per page (default is 20)
        return: returs a dictionary of the users, false if there is an error
        """
        data = {'page': page, 'per_page': per_page}
        if search:
            data['search'] = search
        request = requests.get(self.users_url, params=data,
                               headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def getuser(self, id_):
        """
        Get info for a user identified by id
        :param id_: id of the user
        :return: False if not found, a dictionary if found
        """
        request = requests.get(self.users_url + "/" + str(id_),
                               headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def createuser(self, name, username, password, email, **kwargs):
        """
        Create a user
        :param name: Obligatory
        :param username: Obligatory
        :param password: Obligatory
        :param email: Obligatory
        :param kwargs: Any param the the Gitlab API supports
        :return: True if the user was created,false if it wasn't(already exists)
        """
        data = {"name": name, "username": username, "password": password, "email": email}

        if kwargs:
            data.update(kwargs)

        request = requests.post(self.users_url, headers=self.headers, data=data, 
                                verify=self.verify_ssl)
        if request.status_code == 201:
            return json.loads(request.content.decode("utf-8"))
        elif request.status_code == 404:
            return False

    def deleteuser(self, id_):
        """
        Deletes an user by ID
        :param id_: id of the user to delete
        :return: True if it deleted, False if it couldn't. False could happen
        for several reasons, but there isn't a
        good way of differenting them
        """
        request = requests.delete(self.users_url + "/" + str(id_),
                                  headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return True
        else:
            
            return False

    def currentuser(self):
        """
        Returns the current user parameters. The current user is linked
        to the secret token
        :return: a list with the current user properties
        """
        request = requests.get(self.host + "/api/v3/user",
                               headers=self.headers, verify=self.verify_ssl)
        return json.loads(request.content.decode("utf-8"))

    def edituser(self, id_, **kwargs):
        """
        Edits an user data. Unfortunately we have to check ALL the params,
        as they can't be empty or the user will get all their data empty,
        so we only send the filled params
        :param id_: id of the user to change
        :param kwargs: Any param the the Gitlab API supports
        :return: Dict of the user
        """
        data = {}

        if kwargs:
            data.update(kwargs)

        request = requests.put(self.users_url + "/" + str(id_),
                               headers=self.headers, data=data,
                               verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def getsshkeys(self):
        """
        Gets all the ssh keys for the current user
        :return: a dictionary with the lists
        """
        request = requests.get(self.keys_url, headers=self.headers,
                               verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            
            return False

    def getsshkey(self, id_):
        """
        Get a single ssh key identified by id_
        :param id_: the id of the key
        :return: the key itself
        """
        request = requests.get(self.keys_url + "/" + str(id_),
                               headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            
            return False

    def addsshkey(self, title, key, sudo=""):
        """
        Add a new ssh key for the current user
        :param title: title of the new key
        :param key: the key itself
        :return: true if added, false if it didn't add it
        (it could be because the name or key already exists)
        """
        data = {"title": title, "key": key}
        if sudo != "":
            data['sudo'] = sudo
        request = requests.post(self.keys_url, headers=self.headers, data=data, 
                                verify=self.verify_ssl)
        if request.status_code == 201:
            return True
        else:
            
            return False

    def addsshkeyuser(self, id_, title, key, sudo=""):
        """
        Add a new ssh key for the user identified by id
        :param id_: id of the user to add the key to
        :param title: title of the new key
        :param key: the key itself
        :return: true if added, false if it didn't add it
        (it could be because the name or key already exists)
        """
        data = {"title": title, "key": key}
        if sudo != "":
            data['sudo'] = sudo
        request = requests.post(self.users_url + "/" + str(id_) + "/keys",
                                headers=self.headers, data=data, verify=self.verify_ssl)
        if request.status_code == 201:
            return True
        else:
            
            return False

    def deletesshkey(self, id_):
        """
        Deletes an sshkey for the current user identified by id
        :param id_: the id of the key
        :return: False if it didn't delete it, True if it was deleted
        """
        request = requests.delete(self.keys_url + "/" + str(id_),
                                  headers=self.headers, verify=self.verify_ssl)
        if request.content == b"null":            
            return False
        else:
            return True

    def getprojects(self, page=1, per_page=20, sudo=""):
        """
        Returns a dictionary of all the projects
        :param page: Which page to return (default is 1)
        :param per_page: Number of items to return per page (default is 20)
        :return: list with the repo name, description, last activity,
         web url, ssh url, owner and if its public
        """
        data = {'page': page, 'per_page': per_page}
        if sudo != "":
            data['sudo'] = sudo
        request = requests.get(self.projects_url, params=data,
                               headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def getallprojectsuser(self, per_request=20, sudo=""):
        """
        Returns a list of dictionaries of all the projects visable for that user
        :param per_request: Number of items to return per api request (default is 20)
        :return: list with the repo name, description, last activity,
         web url, ssh url, owner and if its public
        """
        data = {'page': 1, 'per_page': per_request}
        if sudo != "":
            data['sudo'] = sudo
        request = requests.get(self.projects_url, params=data,
                                   headers=self.headers, verify=self.verify_ssl)
        while True:
            if request.status_code == 200:
                list = json.loads(request.content.decode("utf-8"))

                for item in list:
                    yield item
            if 'next' in request.links.keys():
                request = requests.get(request.links['next']['url'],
                                   headers=self.headers, verify=self.verify_ssl)
            else:
                break

    def getallprojects(self, page=1, per_page=20, sudo=""):
        """
        Returns a dictionary of all the projects for admins only
        :param page: Which page to return (default is 1)
        :param per_page: Number of items to return per page (default is 20)
        :return: list with the repo name, description, last activity,
         web url, ssh url, owner and if its public
        """
        data = {'page': page, 'per_page': per_page}
        if sudo != "":
            data['sudo'] = sudo
        request = requests.get(self.projects_url + '/all', params=data,
                               headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def getownprojects(self, page=1, per_page=20, sudo=""):
        """
        Returns a dictionary of all the projects for the current user
        :param page: Which page to return (default is 1)
        :param per_page: Number of items to return per page (default is 20)
        :return: list with the repo name, description, last activity,
         web url, ssh url, owner and if its public
        """
        data = {'page': page, 'per_page': per_page}
        if sudo != "":
            data['sudo'] = sudo
        request = requests.get(self.projects_url + '/owned', params=data,
                               headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def getproject(self, id_):
        """
        Get info for a project identified by id
        :param id_: id of the project
        :return: False if not found, a dictionary if found
        """
        request = requests.get(self.projects_url + "/" + str(id_),
                               headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            
            return False

    def getprojectevents(self, id_, page=1, per_page=20):
        """
        Get the project identified by id, events(commits)
        :param id_: id of the project
        :param page: Which page to return (default is 1)
        :param per_page: Number of items to return per page (default is 20)
        :return: False if no project with that id, a dictionary
         with the events if found
        """
        data = {'page': page, 'per_page': per_page}
        request = requests.get(self.projects_url + "/" + str(id_) +
                               "/events", params=data, headers=self.headers, 
                               verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            
            return False

    def createproject(self, name, namespace_id=None, description="",
                      issues_enabled=0, wall_enabled=0,
                      merge_requests_enabled=0, wiki_enabled=0,
                      snippets_enabled=0, public=0, visibility_level=-1,
                      sudo="", import_url=""):
        """
        Create a project
        :param name: Obligatory
        :return: Dict of information on the newly created project if successful,
         False otherwise
        """
        data = {"name": name, "description": description,
                 "issues_enabled": issues_enabled, "wall_enabled": wall_enabled,
                 "merge_requests_enabled": merge_requests_enabled,
                 "wiki_enabled": wiki_enabled,
                 "snippets_enabled": snippets_enabled,
                 "import_url": import_url}
        if namespace_id != None:
            data['namespace_id'] = namespace_id
        if sudo != "":
            data['sudo'] = sudo

        # to define repository visibilty to other users, in gitlab version 6
        # there is a public option and in gitlab version 7 there is a
        # visibility_level option for the project creation.
        if type(public) != int:
            raise TypeError
        if type(visibility_level) != int:
            if type(visibility_level) == str:
                if visibility_level.lower() == "private":
                    visibility_level = 0
                elif visibility_level.lower() == "internal":
                    visibility_level = 10
                elif visibility_level.lower() == "public":
                    visibility_level = 20
                else:
                    raise ValueError
            else:
                raise TypeError

        if visibility_level > 0:
            if public != 0:
                raise ValueError('Only one of public and visibility_level arguments may be provided')
            data['visibility_level'] =  visibility_level

        if public != 0:
            data['public'] = public

        request = requests.post(self.projects_url, headers=self.headers,
                                data=data, verify=self.verify_ssl)
        if request.status_code == 201:
            return json.loads(request.content.decode("utf-8"))
        elif request.status_code == 403:
            if "Your own projects limit is 0" in request.text:
                print(request.text)
                return False
        else:
            
            return False

    def deleteproject(self, project_id):
        """
        Delete a project
        :param id_: project id
        :return: always true
        """
        request = requests.delete(self.projects_url + "/" + str(project_id),
                                  headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return True

    def createprojectuser(self, id_, name, description="", default_branch="",
                          issues_enabled=0, wall_enabled=0,
                          merge_requests_enabled=0, wiki_enabled=0,
                          snippets_enabled=0, sudo=""):
        """
        Create a project for the given user identified by id
        :param id_: id of the user to crete the project for
        :param name: Obligatory
        :return: True if it created the project, False otherwise
        """
        data = {"name": name, "description": description,
                "default_branch": default_branch,
                "issues_enabled": issues_enabled, "wall_enabled": wall_enabled,
                "merge_requests_enabled": merge_requests_enabled,
                "wiki_enabled": wiki_enabled,
                "snippets_enabled": snippets_enabled}
        if sudo != "":
            data['sudo'] = sudo
        request = requests.post(self.projects_url + "/user/" + str(id_),
                                headers=self.headers, data=data, verify=self.verify_ssl)
        if request.status_code == 201:
            return True
        else:
            
            return False

    def listprojectmembers(self, id_, query=None, page=1, per_page=20):
        """
        lists the members of a given project id
        :param id_: the project id
        :param query: Optional search query
        :param page: Which page to return (default is 1)
        :param per_page: Number of items to return per page (default is 20)
        :return: the projects memebers, false if there is an error
        """
        data = {'page': page, 'per_page': per_page}
        if query:
            data['query'] = query
        request = requests.get(self.projects_url + "/" + str(id_) + "/members",
                               params=data, headers=self.headers,
                               verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            
            return False

    def addprojectmember(self, id_, user_id, access_level, sudo=""):
        # check the access level and put into a number
        """
        adds a project member to a project
        :param id_: project id
        :param user_id: user id
        :param access_level: access level, see gitlab help to know more
        :param sudo: do the request with another user
        :return: True if success
        """
        if access_level.lower() == "master":
            access_level = 40
        elif access_level.lower() == "developer":
            access_level = 30
        elif access_level.lower() == "reporter":
            access_level = 20
        else:
            access_level = 10
        data = {"id": id_, "user_id": user_id, "access_level": access_level}
        if sudo != "":
            data['sudo'] = sudo
        request = requests.post(self.projects_url + "/" + str(id_) + "/members",
                                headers=self.headers, data=data, verify=self.verify_ssl)
        if request.status_code == 201:
            return True
        else:
            return False

    def editprojectmember(self, id_, user_id, access_level, sudo=""):
        """
        edit a project member
        :param id_: project id
        :param user_id: user id
        :param access_level: access level
        :param sudo: do the request as another user
        :return: True if success
        """
        if access_level.lower() == "master":
            access_level = 40
        elif access_level.lower() == "developer":
            access_level = 30
        elif access_level.lower() == "reporter":
            access_level = 20
        else:
            access_level = 10
        data = {"id": id_, "user_id": user_id,
                "access_level": access_level}
        if sudo != "":
            data['sudo'] = sudo
        request = requests.put(self.projects_url + "/" + str(id_) + "/members/"
                               + str(user_id), headers=self.headers, data=data,
                               verify=self.verify_ssl)
        if request.status_code == 200:
            return True
        else:
            
            return False

    def deleteprojectmember(self, id_, user_id):
        """
        Delete a project member
        :param id_: project id
        :param user_id: user id
        :return: always true
        """
        request = requests.delete(self.projects_url + "/" + str(id_)
                                  + "/members/" + str(user_id),
                                  headers=self.headers,
                                  verify=self.verify_ssl)
        if request.status_code == 200:
            return True  # It always returns true

    # TODO: hooks are now system wide and under the /hooks url
    # TODO: change all the hooks methods, not valid anymore
    # TODO: write tests for the hooks
    def getprojecthooks(self, id_):
        """
        get all the hooks from a project
        :param id_: project id
        :return: the hooks
        """
        request = requests.get(self.projects_url + "/" + str(id_) + "/hooks",
                               headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def getprojecthook(self, id_, hook_id):
        """
        get a particular hook from a project
        :param id_: project id
        :param hook_id: hook id
        :return: the hook
        """
        request = requests.get(self.projects_url + "/" + str(id_) + "/hooks/" +
                               str(hook_id), headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            
            return False

    def addprojecthook(self, id_, url):
        """
        add a hook to a project
        :param id_: project id
        :param url: url of the hook
        :return: True if success
        """
        data = {"id": id_, "url": url}
        request = requests.post(self.projects_url + "/" + str(id_) + "/hooks",
                                headers=self.headers, data=data, verify=self.verify_ssl)
        if request.status_code == 201:
            return True
        else:
            return False

    def editprojecthook(self, id_, hook_id, url, sudo=""):
        """
        edit an existing hook from a project
        :param id_: project id
        :param hook_id: hook id
        :param url: the new url
        :param sudo: do the request as another user
        :return: True if success
        """
        data = {"id": id_, "hook_id": hook_id, "url": url}
        if sudo != "":
            data['sudo'] = sudo
        request = requests.put(self.projects_url + "/" + str(id_) + "/hooks/" +
                               str(hook_id), headers=self.headers,
                               data=data, verify=self.verify_ssl)
        if request.status_code == 200:
            return True
        else:
            return False

    def deleteprojecthook(self, id_, hook_id):
        """
        delete a project hook
        :param id_: project id
        :param hook_id: hook id
        :return: True if success
        """
        request = requests.delete(self.projects_url + "/" + str(id_)
                                  + "/hooks/"
                                  + str(hook_id), headers=self.headers,
                                  verify=self.verify_ssl)
        if request.status_code == 200:
            return True
        else:
            return False

    def getsystemhooks(self):
        """
        Get all system hooks
        :return: list of hooks
        """
        request = requests.get(self.hook_url, headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def addsystemhook(self, url):
        """
        add a hook to a project
        :param url: url of the hook
        :return: True if success
        """
        data = {"url": url}
        request = requests.post(self.hook_url, headers=self.headers,
                                data=data, verify=self.verify_ssl)
        if request.status_code == 201:
            return True
        else:
            return False

    def testsystemhook(self, hook_id):
        """
        Test a system hook
        :param hook_id: hook id
        :return: list of hooks
        """
        data = {"id": hook_id}
        request = requests.get(self.hook_url, data=data,
                               headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def deletesystemhook(self, hook_id):
        """
        delete a project hook
        :param hook_id: hook id
        :return: True if success
        """
        data = {"id": hook_id}
        request = requests.delete(self.hook_url + "/{}".format(hook_id), data=data,
                                  headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return True
        else:
            return False

    def listbranches(self, id_):
        """
        list all the branches from a project
        :param id_: project id
        :return: the branches
        """
        request = requests.get(self.projects_url + "/" + str(id_) +
                               "/repository/branches", headers=self.headers,
                               verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def listbranch(self, id_, branch):
        """
        list one branch from a project
        :param id_: project id
        :param branch: branch id
        :return: the branch
        """
        request = requests.get(self.projects_url + "/" + str(id_) +
                               "/repository/branches/" + str(branch),
                               headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def createbranch(self, id_, branch, ref):
        """
        Create branch from commit SHA or existing branch
        :param id_:  The ID of a project
        :param branch: The name of the branch
        :param ref: Create branch from commit SHA or existing branch
        :return: True if success, False if not
        """
        data = {"id": id_, "branch_name": branch, "ref": ref}

        request = requests.post(self.projects_url + "/" + str(id_) +
                                "/repository/branches", headers=self.headers,
                                data=data, verify=self.verify_ssl)
        if request.status_code == 201:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def deletebranch(self, id_, branch):
        """
        Delete branch by name
        :param id_:  The ID of a project
        :param branch: The name of the branch
        :return: True if success, False if not
        """

        request = requests.delete(self.projects_url + "/" + str(id_) +
                                  "/repository/branches/" + str(branch),
                                  headers=self.headers, verify=self.verify_ssl)

        if request.status_code == 200:
            return True
        else:
            return False

    def protectbranch(self, id_, branch):
        """
        protect a branch from changes
        :param id_: project id
        :param branch: branch id
        :return: True if success
        """
        request = requests.put(self.projects_url + "/" + str(id_) +
                               "/repository/branches/" + str(branch) +
                               "/protect", headers=self.headers,
                               verify=self.verify_ssl)
        if request.status_code == 200:
            return True
        else:
            return False

    def unprotectbranch(self, id_, branch):
        """
        stop protecting a branch
        :param id_: project id
        :param branch: branch id
        :return: true if success
        """
        request = requests.put(self.projects_url + "/" + str(id_) +
                               "/repository/branches/" + str(branch) +
                               "/unprotect", headers=self.headers,
                               verify=self.verify_ssl)
        if request.status_code == 200:
            return True
        else:
            
            return False

    def createforkrelation(self, id_, from_):
        """
        create a fork relation. This DO NOT create a fork but only adds
        the relation between 2 repositories
        :param id_: project id
        :param from_: from id
        :return: true if success
        """
        data = {"id": id_, "forked_from_id": from_}
        request = requests.post(self.projects_url + "/" + str(id_) +
                                "/fork/" + str(from_), headers=self.headers,
                                data=data, verify=self.verify_ssl)
        if request.status_code == 201:
            return True
        else:
            
            return False

    def removeforkrelation(self, id_):
        """
        remove an existing fork relation. this DO NOT remove the fork,
        only the relation between them
        :param id_: project id
        :return: true if success
        """
        request = requests.delete(self.projects_url + "/" + str(id_) +
                                  "/fork", headers=self.headers,
                                  verify=self.verify_ssl)
        if request.status_code == 200:
            return True
        else:
            
            return False

    def getissues(self, page=1, per_page=20, sudo=""):
        """
        Return a global list of issues for your user.
        :param page: Which page to return (default is 1)
        :param per_page: Number of items to return per page (default is 20)
        """
        data = {'page': page, 'per_page': per_page}
        if sudo != "":
            data['sudo'] = sudo
        request = requests.get(self.host + "/api/v3/issues",
                               params=data, headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            
            return False

    def getprojectissues(self, id_, page=1, per_page=20, sudo=""):
        """
        Return a list of issues for project id_.
        :param id_: The id for the project.
        :param page: Which page to return (default is 1)
        :param per_page: Number of items to return per page (default is 20)
        """
        data = {'page': page, 'per_page': per_page}
        if sudo != "":
            data['sudo'] = sudo
        request = requests.get(self.projects_url + "/" + str(id_) +
                               "/issues", params=data, headers=self.headers,
                               verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            
            return False

    def getprojectissue(self, id_, issue_id):
        """
        get an specific issue id from a project
        :param id_: project id
        :param issue_id: issue id
        :return: the issue
        """
        request = requests.get(self.projects_url + "/" + str(id_) +
                               "/issues/" + str(issue_id), headers=self.headers, 
                               verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            
            return False

    def createissue(self, id_, title, **kwargs):
        """
        create a new issue
        :param id_: project id
        :param title: title of the issue
        :return: dict with the issue created
        """
        data = {"id": id, "title": title}
        if kwargs:
            data.update(kwargs)
        request = requests.post(self.projects_url + "/" + str(id_) + "/issues",
                                headers=self.headers, data=data, verify=self.verify_ssl)
        if request.status_code == 201:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def editissue(self, id_, issue_id, **kwargs):
        """
        edit an existing issue data
        :param id_: project id
        :param issue_id: issue id
        :return: true if success
        """
        data = {"id": id_, "issue_id": issue_id}
        if kwargs:
            data.update(kwargs)
        request = requests.put(self.projects_url + "/" + str(id_) + "/issues/" +
                               str(issue_id), headers=self.headers,
                               data=data, verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def getmilestones(self, id_):
        """
        get the milestones for a project
        :param id_: project id
        :return: the milestones
        """
        request = requests.get(self.projects_url + "/" + str(id_) +
                               "/milestones", headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            
            return False

    def getmilestone(self, id_, milestone_id):
        """
        get an specific milestone
        :param id_: project id
        :param milestone_id: milestone id
        :return: the milestone
        """
        request = requests.get(self.projects_url + "/" + str(id_)
                               + "/milestones/"
                               + str(milestone_id), headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            
            return False

    def createmilestone(self, id_, title, description="", due_date="", sudo=""):
        """
        create a new milestone
        :param id_: project id
        :param title: title
        :param description: description
        :param due_date: due date
        :param sudo: do the request as another user
        :return: true if success
        """
        data = {"id": id_, "title": title, "description": description,
                "due_date": due_date}
        if sudo != "":
            data['sudo'] = sudo
        request = requests.post(self.projects_url + "/" + str(id_) +
                                "/milestones", headers=self.headers, data=data, 
                                verify=self.verify_ssl)
        if request.status_code == 201:
            return json.loads(request.content.decode("utf-8"))
        else:
            
            return False

    def editmilestone(self, id_, milestone_id, title="", description="",
                      due_date="", state_event="", sudo=""):
        """
        edit an existing milestone
        :param id_: project id
        :param milestone_id: milestone id
        :param title: title
        :param description: description
        :param due_date: due date
        :param state_event: state
        :param sudo: do the request as another user
        :return: true if success
        """
        data = {"id": id_, "milestone_id": milestone_id, "title": title,
                "description": description,
                "due_date": due_date, "state_event": state_event}
        if sudo != "":
            data['sudo'] = sudo
        request = requests.put(self.projects_url + "/" + str(id_)
                               + "/milestones/"
                               + str(milestone_id), headers=self.headers,
                               data=data, verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            
            return False

    def listdeploykeys(self, id_):
        """
        Get a list of a project's deploy keys.
        :param id_: project id
        :return: the keys in a dictionary if success, false if not
        """
        request = requests.get(self.projects_url + "/" + str(id_) + "/keys",
                               headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            
            return False

    def listdeploykey(self, id_, key_id):
        """
        Get a single key.
        :param id_: project id
        :param key_id: key id
        :return: the key in a dict if success, false if not
        """
        request = requests.get(self.projects_url + "/" + str(id_) + "/keys/" +
                               str(key_id), headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            
            return False

    def adddeploykey(self, id_, title, key, sudo=""):
        """
        Creates a new deploy key for a project.
        If deploy key already exists in another project - it will be joined
        to project but only if original one was is accessible by same user
        :param id_: project id
        :param title: title of the key
        :param key: the key itself
        :return: true if sucess, false if not
        """
        data = {"id": id_, "title": title, "key": key}
        if sudo != "":
            data['sudo'] = sudo
        request = requests.post(self.projects_url + "/" + str(id_) + "/keys",
                                headers=self.headers, data=data, verify=self.verify_ssl)
        if request.status_code == 201:
            return True
        else:
            
            return False

    def deletedeploykey(self, id_, key_id):
        """
        Delete a deploy key from a project
        :param id_: project id
        :param key_id: key id to delete
        :return: true if success, false if not
        """
        request = requests.delete(self.projects_url + "/" + str(id_) + "/keys/"
                                  + str(key_id), headers=self.headers,
                                  verify=self.verify_ssl)
        if request.status_code == 200:
            return True
        else:
            
            return False

    def getreadme(self, repo, mark=False):
        """
        returns the readme
        :param mark: If false returns the raw readme,
        else returns the readme parsed by markdown
        :param repo: the web url to the project
        """
        request = requests.get(repo + "/raw/master/README.md?private_token=" +
                               self.token, verify=self.verify_ssl)  # setting the headers doesn't work
        if b"<!DOCTYPE html>" in request.content:  # having HTML means a 404
            if mark:
                return "<p>There isn't a README.md for that project</p>"
            else:
                return "There isn't a README.md for that project"
        else:
            if mark:
                try: 
                    return markdown.markdown(request.content.decode('utf-8'))
                except Exception as e:
                    return request.content.decode('utf-8')
            else:
                return request.content.decode('utf-8')

    def creategroup(self, name, path):
        """
        Creates a new group
        :param name: The name of the group
        :param path: The path for the group
        """
        request = requests.post(self.groups_url,
                                data={'name': name, 'path': path},
                                headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 201:
            return True
        else:
            msg = json.loads(request.content.decode("utf-8"))['message']
            return exceptions.HttpError(msg)

    def getgroups(self, id_=None, page=1, per_page=20, sudo=""):
        """
        Retrieve group information
        :param id_: Specify a group. Otherwise, all groups are returned
        :param page: Which page to return (default is 1)
        :param per_page: Number of items to return per page (default is 20)
        """
        data = {'page': page, 'per_page': per_page}
        if sudo != "":
            data['sudo'] = sudo
        request = requests.get("{0}/{1}".format(self.groups_url,
                                                id_ if id_ else ""),
                               params=data, headers=self.headers,
                               verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            
            return False

    def moveproject(self, group_id, project_id):
        """
        Move a given project into a given group
        :param group_id: ID of the destination group
        :param project_id: ID of the project to be moved
        """
        request = requests.post("{0}/{1}/projects/{2}".format(self.groups_url,
                                                              group_id,
                                                              project_id),
                                headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 201:
            return True
        else:
            
            return False

    def getmergerequests(self, project_id, page=1, per_page=20, state=None, sudo=""):
        """
        Get all the merge requests for a project.
        :param project_id: ID of the project to retrieve merge requests for
        :param page: If pagination is set, which page to return
        :param state: Passes merge request state to filter them by it
        :param per_page: Number of merge requests to return per page
        """
        data = {'page': page, 'per_page': per_page, 'state': state}
        if sudo != "":
            data['sudo'] = sudo
        url_str = '{0}/{1}/merge_requests'.format(self.projects_url, project_id)
        request = requests.get(url_str, params=data, headers=self.headers,
                               verify=self.verify_ssl)

        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            
            return False

    def getmergerequest(self, project_id, mergerequest_id):
        """
        Get information about a specific merge request.
        :type project_id: int
        :param project_id: ID of the project
        :param mergerequest_id: ID of the merge request
        """
        url_str = '{0}/{1}/merge_request/{2}'.format(self.projects_url,
                                                     project_id,
                                                     mergerequest_id)
        request = requests.get(url_str, headers=self.headers, verify=self.verify_ssl)

        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            
            return False

    def getmergerequestcomments(self, project_id, mergerequest_id, page=1, per_page=20):
        """
        Get comments of a merge request.
        :type project_id: int
        :param project_id: ID of the project
        :param mergerequest_id: ID of the merge request
        """
        url_str = '{0}/{1}/merge_request/{2}/comments'.format(self.projects_url,
                                                     project_id,
                                                     mergerequest_id)
        data = {'page': page, 'per_page': per_page}
        request = requests.get(url_str, params=data, headers=self.headers, verify=self.verify_ssl)

        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:

            return False

    def createmergerequest(self, project_id, sourcebranch, targetbranch,
                           title, target_project_id=None, assignee_id=None, sudo=""):
        """
        Create a new merge request.
        :param project_id: ID of the project originating the merge request
        :param sourcebranch: name of the branch to merge from
        :param targetbranch: name of the branch to merge to
        :param title: Title of the merge request
        :param assignee_id: Assignee user ID
        """
        url_str = '{0}/{1}/merge_requests'.format(self.projects_url, project_id)
        data = {'source_branch': sourcebranch,
                'target_branch': targetbranch,
                'title': title,
                'assignee_id': assignee_id,
                'target_project_id': target_project_id}
        if sudo != "":
            data['sudo'] = sudo

        request = requests.post(url_str, data=data, headers=self.headers, 
                                verify=self.verify_ssl)
        if request.status_code == 201:
            return json.loads(request.content.decode("utf-8"))
        else:
            
            return False

    def updatemergerequest(self, project_id, mergerequest_id, sourcebranch=None,
                           targetbranch=None, title=None,
                           assignee_id=None, closed=None, sudo=""):
        """
        Update an existing merge request.
        :param project_id: ID of the project originating the merge request
        :param mergerequest_id: ID of the merge request to update
        :param sourcebranch: name of the branch to merge from
        :param targetbranch: name of the branch to merge to
        :param title: Title of the merge request
        :param assignee_id: Assignee user ID
        :param closed: MR status.  True = closed
        """
        url_str = '{0}/{1}/merge_request/{2}'.format(self.projects_url,
                                                     project_id,
                                                     mergerequest_id)
        data = {'source_branch': sourcebranch,
                'target_branch': targetbranch,
                'title': title,
                'assignee_id': assignee_id,
                'closed': closed}
        if sudo != "":
            data['sudo'] = sudo

        request = requests.post(url_str, data=data, headers=self.headers, 
                                verify=self.verify_ssl)
        if request.status_code == 201:
            return True
        else:
            
            return False

    def acceptmergerequest(self, project_id, mergerequest_id, merge_commit_message=None, sudo=""):
        """
        Update an existing merge request.
        :param project_id: ID of the project originating the merge request
        :param mergerequest_id: ID of the merge request to accept
        :param merge_commit_message: Custom merge commit message
        """
        url_str = '{0}/{1}/merge_request/{2}/merge'.format(self.projects_url,
                                                           project_id,
                                                           mergerequest_id)

        data = {'merge_commit_message': merge_commit_message}
        if sudo != "":
            data['sudo'] = sudo

        request = requests.put(url_str, data=data, headers=self.headers,
                               verify=self.verify_ssl)
        if request.status_code == 200:
            return True
        else:
            msg = request.headers['status']
            raise exceptions.HttpError(msg)

    def addcommenttomergerequest(self, project_id, mergerequest_id, note):
        """
        Add a comment to a merge request.
        :param project_id: ID of the project originating the merge request
        :param mergerequest_id: ID of the merge request to comment on
        :param note: Text of comment
        """
        url_str = '{0}/{1}/merge_request/{2}/comments'.format(self.projects_url,
                                                              project_id,
                                                              mergerequest_id)
        request = requests.post(url_str, data={'note': note},
                                headers=self.headers, verify=self.verify_ssl)

        if request.status_code == 201:
            return True
        else:
            
            return False

    def getsnippets(self, project_id):
        """
        Get all the snippets of the project identified by project_id
        @param project_id: project id to get the snippets from
        @return: list of dictionaries
        """
        request = requests.get(self.projects_url + "/" + str(project_id) + "/snippets",
                               verify=self.verify_ssl, headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def getsnippet(self, project_id, snippet_id):
        """
        Get one snippet from a project
        @param project_id: project id to get the snippet from
        @param snippet_id: snippet id
        @return: dictionary
        """
        request = requests.get(self.projects_url + "/" + str(project_id) + "/snippets/" + str(snippet_id),
                               verify=self.verify_ssl, headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content.decode('utf-8'))
        else:
            return False

    def createsnippet(self, project_id, title, file_name, code, lifetime=""):
        """
        Creates an snippet
        @param project_id: project id to create the snippet under
        @param title: title of the snippet
        @param file_name: filename for the snippet
        @param code: content of the snippet
        @param lifetime: expiration date
        @return: True if correct, false if failed
        """
        data = {"id": project_id, "title": title, "file_name": file_name, "code": code}
        if lifetime != "":
            data["lifetime"] = lifetime
        request = requests.post(self.projects_url + "/" + str(project_id) + "/snippets",
                                data=data, verify=self.verify_ssl, headers=self.headers)
        if request.status_code == 201:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def getsnippetcontent(self, project_id, snippet_id):
        request = requests.get(self.projects_url + "/" + str(project_id) +
                               "/snippets/" + str(snippet_id) + "/raw",
                               verify=self.verify_ssl, headers=self.headers)
        if request.status_code == 200:
            return request.content.decode("utf-8")
        else:
            return False

    def deletesnippet(self, project_id, snippet_id):
        request = requests.delete(self.projects_url + "/" + str(project_id) +
                                  "/snippets/" + str(snippet_id), headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return True
        else:
            return False

    def getrepositories(self, project_id):
        request = requests.get(self.projects_url + "/" + str(project_id) + "/repository/branches",
                               verify=self.verify_ssl, headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def getrepositorybranch(self, project_id, branch):
        request = requests.get(self.projects_url + "/" + str(project_id) +
                               "/repository/branches/" + str(branch),
                               verify=self.verify_ssl, headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        elif request.status_code == 404:
            if json.loads(request.content.decode("utf-8"))['message'] == "404 Branch does not exist Not Found":
                # In the future we should raise an exception here
                return False
        else:
            return False

    def protectrepositorybranch(self, project_id, branch_name):
        request = requests.put(self.projects_url + "/" + str(project_id) +
                               "/repository/branches/" + str(branch_name) + "/protect",
                               headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def unprotectrepositorybranch(self, project_id, branch_name):
        request = requests.put(self.projects_url + "/" + str(project_id) +
                               "/repository/branches/" + str(branch_name) + "/unprotect",
                               headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return

    def listrepositorytags(self, project_id):
        request = requests.get(self.projects_url + "/" + str(project_id) +
                               "/repository/tags", verify=self.verify_ssl,
                               headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def listrepositorycommits(self, project_id,  page=1, per_page=20):
        
        data = {'page': page, 'per_page': per_page}
        request = requests.get(self.projects_url + "/" + str(project_id) +
                               "/repository/commits", verify=self.verify_ssl,
                               params=data, headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def listrepositorycommit(self, project_id, sha1):
        request = requests.get(self.projects_url + "/" + str(project_id) +
                               "/repository/commits/" + str(sha1),
                               verify=self.verify_ssl, headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def listrepositorycommitdiff(self, project_id, sha1):
        request = requests.get(self.projects_url + "/" + str(project_id) +
                               "/repository/commits/" + str(sha1) + "/diff",
                               verify=self.verify_ssl, headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def listrepositorytree(self, project_id, path="", ref_name=""):
        data = {}
        if path != "":
            data['path'] = path
        if ref_name != "":
            data['ref_name'] = ref_name

        request = requests.get(self.projects_url + "/" + str(project_id) +
                               "/repository/tree/", params=data,
                               verify=self.verify_ssl, headers=self.headers)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def getrawblob(self, project_id, sha1, path):
        data = {"filepath": path}

        request = requests.get(self.projects_url + "/" + str(project_id) +
                               "/repository/blobs/" + str(sha1),
                               params=data, verify=self.verify_ssl,
                               headers=self.headers)
        if request.status_code == 200:
            return request.content.decode("utf-8")
        else:
            return False

    def compare_branches_tags_commits(self, project_id, from_id, to_id):
        """
        Compare branches, tags or commits
        :param project_id: The ID of a project
        :param from_id: the commit sha or branch name
        :param to_id: the commit sha or branch name
        return commit list and diff between two branches tags or commits provided by name
        hash value
        """
        data = {"from":from_id, "to":to_id}
        request = requests.get(self.projects_url + "/" + str(project_id) +
                               "/repository/compare/",
                               params=data, verify=self.verify_ssl,
                               headers=self.headers)

        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def searchproject(self, search, page=1, per_page=20):
        """
        projects section
        """
        data = {'page': page, 'per_page': per_page}
        request = requests.get(self.search_url + str(search), params=data,
                               verify=self.verify_ssl, headers=self.headers)

        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            msg = json.loads(request.content.decode("utf-8"))['message']
            raise exceptions.HttpError(msg)

    def getfilearchive(self, project_id, filepath="", sha1=""):
        """
        repository section
        """
        request = requests.get(self.projects_url + "/" + str(project_id) +
                               "/repository/archive", verify=self.verify_ssl,
                               headers=self.headers)
        if request.status_code == 200:
            if filepath == "":
                filepath = request.headers['content-disposition'].split(";")[1].split("=")[1].strip('"')
            with open(filepath, "wb") as filesave:
                filesave.write(request.content)
                # TODO: Catch oserror exceptions as no permissions and such
                # TODO: change the filepath to a path and keep always the filename?
            return True
        else:
            msg = json.loads(request.content.decode("utf-8"))['message']
            raise exceptions.HttpError(msg)

    def deletegroup(self, group_id):
        """
        groups section, new in 6.2

        Deletes an group by ID
        :param id_: id of the group to delete
        :return: True if it deleted, False if it couldn't. False could happen
        for several reasons, but there isn't a
        good way of differentiating them
        """
        request = requests.delete(self.groups_url + "/" + str(group_id),
                                  headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return True
        else:
            return False

    def listgroupmembers(self, group_id, page=1, per_page=20):
        """
        list group members
        new in 6.2

        lists the members of a given group id
        :param group_id: the group id
        :param page: which page to return (default is 1)
        :param per_page: number of items to return per page (default is 20)
        :return: the group's members
        """
        data = {'page': page, 'per_page': per_page}
        request = requests.get(self.groups_url + "/" + str(group_id) + "/members", params=data,
                               headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def addgroupmember(self, group_id, user_id, access_level, sudo=""):
        """
        add a user to a group
        new in 6.2

        # check the access level and put into a number

        adds a project member to a project
        :param id_: project id
        :param user_id: user id
        :param access_level: access level, see gitlab help to know more
        :param sudo: do the request with another user
        :return: True if success
        """
        if not isinstance(access_level, int):
            if access_level.lower() == "owner":
                access_level = 50
            elif access_level.lower() == "master":
                access_level = 40
            elif access_level.lower() == "developer":
                access_level = 30
            elif access_level.lower() == "reporter":
                access_level = 20
            elif access_level.lower() == "guest":
                access_level = 10
            else:
                return False

        data = {"id": group_id, "user_id": user_id, "access_level": access_level}
        if sudo != "":
            data['sudo'] = sudo
        request = requests.post(self.groups_url + "/" + str(group_id) + "/members",
                                headers=self.headers, data=data, verify=self.verify_ssl)
        if request.status_code == 201:
            return True
        else:
            return False

    def deletegroupmember(self, group_id, user_id):
        """
        Delete a group member
        :param id_: project id
        :param user_id: user id
        :return: always true
        """
        request = requests.delete(self.groups_url + "/" + str(group_id)
                                  + "/members/" + str(user_id),
                                  headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return True  # It always returns true

    def getprojectwallnotes(self, project_id):
        """
        get the notes from the wall of a project
        """
        request = requests.get(self.projects_url + "/" + str(project_id) + "/notes",
                               verify=self.verify_ssl, headers=self.headers)

        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def getprojectwallnote(self, project_id, note_id):
        """
        get one note from the wall of the project
        """
        request = requests.get(self.projects_url + "/" + str(project_id) + "/notes/" + str(note_id),
                               verify=self.verify_ssl, headers=self.headers)

        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def createprojectwallnote(self, project_id, content):
        """
        create a new note
        """
        data = {"body": content}
        request = requests.post(self.projects_url + "/" + str(project_id) + "/notes",
                                verify=self.verify_ssl, headers=self.headers, data=data)

        if request.status_code == 201:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def getissuewallnotes(self, project_id, issue_id):
        """
        get the notes from the wall of a issue
        """
        request = requests.get(self.projects_url + "/" + str(project_id) + "/issues/" + str(issue_id) + "/notes",
                               verify=self.verify_ssl, headers=self.headers)

        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def getissuewallnote(self, project_id, issue_id, note_id):
        """
        get one note from the wall of the issue
        """
        request = requests.get(self.projects_url + "/" + str(project_id) + "/issues/" + str(issue_id) + "/notes/" + str(note_id),
                               verify=self.verify_ssl, headers=self.headers)

        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def createissuewallnote(self, project_id, issue_id, content):
        """
        create a new note
        """
        data = {"body": content}
        request = requests.post(self.projects_url + "/" + str(project_id) + "/issues/" + str(issue_id) + "/notes",
                                verify=self.verify_ssl, headers=self.headers, data=data)

        if request.status_code == 201:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def getsnippetwallnotes(self, project_id, snippet_id):
        """
        get the notes from the wall of a snippet
        """
        request = requests.get(self.projects_url + "/" + str(project_id) + "/snippets/" + str(snippet_id) + "/notes",
                               verify=self.verify_ssl, headers=self.headers)

        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def getsnippetwallnote(self, project_id, snippet_id, note_id):
        """
        get one note from the wall of the snippet
        """
        request = requests.get(self.projects_url + "/" + str(project_id) + "/snippets/" + str(snippet_id) + "/notes/" + str(note_id),
                               verify=self.verify_ssl, headers=self.headers)

        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def createsnippetewallnote(self, project_id, snippet_id, content):
        """
        create a new note
        """
        data = {"body": content}
        request = requests.post(self.projects_url + "/" + str(project_id) + "/snippets/" + str(snippet_id) + "/notes",
                                verify=self.verify_ssl, headers=self.headers, data=data)

        if request.status_code == 201:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def getmergerequestwallnotes(self, project_id, merge_request_id):
        """
        get the notes from the wall of a merge request
        """
        request = requests.get(self.projects_url + "/" + str(project_id) + "/merge_requests/" + str(merge_request_id) + "/notes",
                               verify=self.verify_ssl, headers=self.headers)

        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def getmergerequestwallnote(self, project_id, merge_request_id, note_id):
        """
        get one note from the wall of the merge request
        """
        request = requests.get(self.projects_url + "/" + str(project_id) + "/merge_requests/" + str(merge_request_id) + "/notes/" + str(note_id),
                               verify=self.verify_ssl, headers=self.headers)

        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def createmergerequestewallnote(self, project_id, merge_request_id, content):
        """
        create a new note
        """
        data = {"body": content}
        request = requests.post(self.projects_url + "/" + str(project_id) + "/merge_requests/" + str(merge_request_id) + "/notes",
                                verify=self.verify_ssl, headers=self.headers, data=data)

        if request.status_code == 201:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def createfile(self, project_id, file_path, branch_name, content, commit_message):
        """
        Creates a new file in the repository
        :param project_id: project id
        :param file_path: Full path to new file. Ex. lib/class.rb
        :param branch_name: The name of branch
        :param content: File content
        :param commit_message: Commit message
        :return: true if success, false if not
        """
        data = {"file_path": file_path, "branch_name": branch_name,
                "content": content, "commit_message": commit_message}
        request = requests.post(self.projects_url + "/" + str(project_id) + "/repository/files",
                                verify=self.verify_ssl, headers=self.headers, data=data)
        if request.status_code == 201:
            return True
        else:
            return False

    def updatefile(self, project_id, file_path, branch_name, content, commit_message):
        """
        Updates an existing file in the repository
        :param project_id: project id
        :param file_path: Full path to new file. Ex. lib/class.rb
        :param branch_name: The name of branch
        :param content: File content
        :param commit_message: Commit message
        :return: true if success, false if not
        """
        data = {"file_path": file_path, "branch_name": branch_name,
                "content": content, "commit_message": commit_message}
        request = requests.put(self.projects_url + "/" + str(project_id) + "/repository/files",
                               headers=self.headers, data=data, verify=self.verify_ssl)

        if request.status_code == 200:
            return True
        else:
            return False

    def getfile(self, project_id, file_path, ref):
        """
        Allows you to receive information about file in repository like name, size, content.
        Note that file content is Base64 encoded.
        :param project_id: project_id
        :param file_path: Full path to file. Ex. lib/class.rb
        :param ref: The name of branch, tag or commit
        :return:
        """
        data = {"file_path": file_path, "ref": ref}
        request = requests.get(self.projects_url + "/" + str(project_id) + "/repository/files",
                               headers=self.headers, data=data, verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            return False

    def deletefile(self, project_id, file_path, branch_name, commit_message):
        """
        Deletes existing file in the repository
        :param project_id: project id
        :param file_path: Full path to new file. Ex. lib/class.rb
        :param branch_name: The name of branch
        :param commit_message: Commit message
        :return: true if success, false if not
        """
        data = {"file_path": file_path, "branch_name": branch_name,
                "commit_message": commit_message}
        request = requests.delete(self.projects_url + "/" + str(project_id) + "/repository/files",
                                  headers=self.headers, data=data,
                                  verify=self.verify_ssl)
        if request.status_code == 200:
            return True
        else:
            return False

    def setgitlabciservice(self, project_id, token, project_url):
        """
        Set GitLab CI service for project
        :param project_id: project id
        :param token: CI project token
        :param project_url: CI project url
        :return: true if success, false if not
        """
        data = {"token": token, "project_url": project_url}
        request = requests.put(self.projects_url + "/" + str(project_id) + "/services/gitlab-ci",
                               verify=self.verify_ssl, headers=self.headers, data=data)

        if request.status_code == 200:
            return True
        else:
            return False

    def deletegitlabciservice(self, project_id, token, project_url):
        """
        Delete GitLab CI service settings
        :return: true if success, false if not
        """
        request = requests.delete(self.projects_url + "/" + str(project_id) + "/services/gitlab-ci",
                                  headers=self.headers, verify=self.verify_ssl)

        if request.status_code == 200:
            return True
        else:
            return False
