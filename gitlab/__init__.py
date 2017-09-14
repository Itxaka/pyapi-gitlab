# -*- coding: utf-8 -*-
"""
pyapi-gitlab, a gitlab python wrapper for the gitlab API
by Itxaka Serrano Garcia <itxakaserrano@gmail.com>
Check the license on the LICENSE file
"""
import requests

from . import exceptions
from .session import Session
from .users import Users
from .keys import Keys
from .helper import deprecated, format_string


class Gitlab(Session, Users, Keys):
    """
    Gitlab class

    On init we setup the token used for all the api calls and all the urls

    :param host: host of gitlab
    :param token: token
    :param verify_ssl: Weather or not to verify the SSL cert
    :param auth: Authentication
    :param timeout: Timeout
    :param suppress_http_error: Use :obj:`False` to unsuppress
        :class:`requests.exceptions.HTTPError` exceptions on failure
    :return: None
    """
    def setsudo(self, user=None):
        """
        Set the subsequent API calls to the user provided

        :param user: User id or username to change to, None to return to the logged user
        :return: Nothing
        """
        if user is None:
            try:
                self.headers.pop('SUDO')
            except KeyError:
                pass
        else:
            self.headers['SUDO'] = user

    def getprojectsowned(self, page=1, per_page=20):
        """
        Returns a dictionary of all the projects for the current user

        :return: list with the repo name, description, last activity, web url, ssh url, owner and if its public
        """
        data = {'page': page, 'per_page': per_page}

        request = requests.get(
            '{0}/owned'.format(self.projects_url), params=data, headers=self.headers,
            verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def get_project(self, project):
        """
        Get info for a project identified by id or namespace/project_name

        :param project: The ID or URL-encoded path of the project
        :return: Dictionary containing the Project
        :raise: HttpError: If invalid response returned
        """
        project = format_string(project)

        return self.get(
            '/projects/{project}'.format(project=project))

    def getproject(self, project_id):
        """Get info for a project identified by id or namespace/project_name

        :param project_id: id or namespace/project_name of the project
        :return: False if not found, a dictionary if found
        """
        return self.get_project(project_id)

    def getprojectevents(self, project_id, page=1, per_page=20):
        """
        Get the project identified by id, events(commits)

        :param project_id: id of the project
        :return: False if no project with that id, a dictionary with the events if found
        """
        data = {'page': page, 'per_page': per_page}
        request = requests.get(
            '{0}/{1}/events'.format(self.projects_url, project_id), params=data,
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def createproject(self, name, **kwargs):
        """
        Creates a new project owned by the authenticated user.

        :param name: new project name
        :param path: custom repository name for new project. By default generated based on name
        :param namespace_id: namespace for the new project (defaults to user)
        :param description: short project description
        :param issues_enabled:
        :param merge_requests_enabled:
        :param wiki_enabled:
        :param snippets_enabled:
        :param public: if true same as setting visibility_level = 20
        :param visibility_level:
        :param sudo:
        :param import_url:
        :return:
        """
        data = {'name': name}

        if kwargs:
            data.update(kwargs)

        request = requests.post(
            self.projects_url, headers=self.headers, data=data,
            verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 201:
            return request.json()
        elif request.status_code == 403:
            if 'Your own projects limit is 0' in request.text:
                print(request.text)
                return False
        else:
            return False

    def editproject(self, project_id, **kwargs):
        """
        Edit an existing project.

        :param name: new project name
        :param path: custom repository name for new project. By default generated based on name
        :param default_branch: they default branch
        :param description: short project description
        :param issues_enabled:
        :param merge_requests_enabled:
        :param wiki_enabled:
        :param snippets_enabled:
        :param public: if true same as setting visibility_level = 20
        :param visibility_level:
        :return:
        """
        data = {"id": project_id}

        if kwargs:
            data.update(kwargs)

        request = requests.put(
            '{0}/{1}'.format(self.projects_url, project_id), headers=self.headers,
            data=data, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return True
        elif request.status_code == 400:
            if "Your param's are invalid" in request.text:
                print(request.text)
                return False
        else:
            return False

    def shareproject(self, project_id, group_id, group_access):
        """
        Allow to share project with group.

        :param project_id: The ID of a project
        :param group_id: The ID of a group
        :param group_access: Level of permissions for sharing
        :return: True is success
        """
        data = {'id': project_id, 'group_id': group_id, 'group_access': group_access}

        request = requests.post(
            '{0}/{1}/share'.format(self.projects_url, project_id),
            headers=self.headers, data=data, verify=self.verify_ssl)

        return request.status_code == 201

    def delete_project(self, id):
        """
        Delete a project from the Gitlab server

        Gitlab currently returns a Boolean True if the deleted and as such we return an
        empty Dictionary

        :param id: The ID of the project or NAMESPACE/PROJECT_NAME
        :return: Dictionary
        :raise: HttpError: If invalid response returned
        """
        url = '/projects/{id}'.format(id=id)

        response = self.delete(url)
        if response is True:
            return {}
        else:
            return response

    @deprecated
    def deleteproject(self, project_id):
        """
        Delete a project

        .. warning:: Warning this is being deprecated please use :func:`gitlab.Gitlab.delete_project`

        :param project_id: project id
        :type project_id: int
        :return: always true
        """
        self.delete_project(project_id)
        return True

    def createprojectuser(self, user_id, name, **kwargs):
        """
        Creates a new project owned by the specified user. Available only for admins.

        :param user_id: user_id of owner
        :param name: new project name
        :param description: short project description
        :param default_branch: 'master' by default
        :param issues_enabled:
        :param merge_requests_enabled:
        :param wiki_enabled:
        :param snippets_enabled:
        :param public: if true same as setting visibility_level = 20
        :param visibility_level:
        :param import_url:
        :param sudo:
        :return:
        """
        data = {'name': name}

        if kwargs:
            data.update(kwargs)

        request = requests.post(
            '{0}/user/{1}'.format(self.projects_url, user_id), headers=self.headers,
            data=data, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 201:
            return True
        else:

            return False

    def getprojectmembers(self, project_id, query=None, page=1, per_page=20):
        """
        Lists the members of a given project id

        :param project_id: the project id
        :param query: Optional search query
        :param page: Which page to return (default is 1)
        :param per_page: Number of items to return per page (default is 20)
        :return: the projects members, false if there is an error
        """
        data = {'page': page, 'per_page': per_page}

        if query:
            data['query'] = query

        request = requests.get(
            '{0}/{1}/members'.format(self.projects_url, project_id),
            params=data, headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def addprojectmember(self, project_id, user_id, access_level):
        """Adds a project member to a project

        :param project_id: project id
        :param user_id: user id
        :param access_level: access level, see gitlab help to know more
        :return: True if success
        """
        # if isinstance(access_level, basestring):
        if access_level.lower() == 'master':
            access_level = 40
        elif access_level.lower() == 'developer':
            access_level = 30
        elif access_level.lower() == 'reporter':
            access_level = 20
        else:
            access_level = 10

        data = {'id': project_id, 'user_id': user_id, 'access_level': access_level}

        request = requests.post(
            '{0}/{1}/members'.format(self.projects_url, project_id),
            headers=self.headers, data=data, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 201:
            return True
        else:
            return False

    def editprojectmember(self, project_id, user_id, access_level):
        """Edit a project member

        :param project_id: project id
        :param user_id: user id
        :param access_level: access level
        :return: True if success
        """
        if access_level.lower() == 'master':
            access_level = 40
        elif access_level.lower() == 'developer':
            access_level = 30
        elif access_level.lower() == 'reporter':
            access_level = 20
        else:
            access_level = 10
        data = {'id': project_id, 'user_id': user_id, 'access_level': access_level}

        request = requests.put(
            '{0}/{1}/members/{2}'.format(self.projects_url, project_id, user_id),
            headers=self.headers, data=data, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return True
        else:
            return False

    def deleteprojectmember(self, project_id, user_id):
        """Delete a project member

        :param project_id: project id
        :param user_id: user id
        :return: always true
        """
        request = requests.delete(
            '{0}/{1}/members/{2}'.format(self.projects_url, project_id, user_id),
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return True  # It always returns true

    def getprojecthooks(self, project_id, page=1, per_page=20):
        """Get all the hooks from a project

        :param project_id: project id
        :param page: Page number
        :param per_page: Records per page
        :return: the hooks
        """
        data = {'page': page, 'per_page': per_page}
        request = requests.get(
            '{0}/{1}/hooks'.format(self.projects_url, project_id), params=data,
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def getprojecthook(self, project_id, hook_id):
        """Get a particular hook from a project

        :param project_id: project id
        :param hook_id: hook id
        :return: the hook
        """
        request = requests.get(
            '{0}/{1}/hooks/{2}'.format(self.projects_url, project_id, hook_id),
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def addprojecthook(self, project_id, url, push=False, issues=False, merge_requests=False, tag_push=False):
        """
        add a hook to a project

        :param project_id: project id
        :param url: url of the hook
        :return: True if success
        """
        data = {
            'id': project_id,
            'url': url,
            'push_events': int(bool(push)),
            'issues_events': int(bool(issues)),
            'merge_requests_events': int(bool(merge_requests)),
            'tag_push_events': int(bool(tag_push)),
        }

        request = requests.post(
            '{0}/{1}/hooks'.format(self.projects_url, project_id),
            headers=self.headers, data=data, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 201:
            return request.json()
        else:
            return False

    def editprojecthook(self, project_id, hook_id, url, push=False, issues=False, merge_requests=False, tag_push=False):
        """
        edit an existing hook from a project

        :param id_: project id
        :param hook_id: hook id
        :param url: the new url
        :return: True if success
        """
        data = {
            "id": project_id,
            "hook_id": hook_id,
            "url": url,
            'push_events': int(bool(push)),
            'issues_events': int(bool(issues)),
            'merge_requests_events': int(bool(merge_requests)),
            'tag_push_events': int(bool(tag_push)),
        }

        request = requests.put(
            '{0}/{1}/hooks/{2}'.format(self.projects_url, project_id, hook_id),
            headers=self.headers, data=data, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return True
        else:
            return False

    def deleteprojecthook(self, project_id, hook_id):
        """
        Delete a project hook

        :param project_id: project id
        :param hook_id: hook id
        :return: True if success
        """
        request = requests.delete(
            '{0}/{1}/hooks/{2}'.format(self.projects_url, project_id, hook_id),
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return True
        else:
            return False

    def getsystemhooks(self, page=1, per_page=20):
        """
        Get all system hooks

        :param page: Page number
        :param per_page: Records per page
        :return: list of hooks
        """
        data = {'page': page, 'per_page': per_page}

        request = requests.get(
            self.hook_url, params=data, headers=self.headers,
            verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def addsystemhook(self, url):
        """
        Add a system hook

        :param url: url of the hook
        :return: True if success
        """
        data = {"url": url}

        request = requests.post(
            self.hook_url, headers=self.headers, data=data,
            verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

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

        request = requests.get(
            self.hook_url, data=data, headers=self.headers,
            verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def deletesystemhook(self, hook_id):
        """
        Delete a project hook

        :param hook_id: hook id
        :return: True if success
        """
        data = {"id": hook_id}

        request = requests.delete(
            '{0}/{1}'.format(self.hook_url, hook_id), data=data,
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return True
        else:
            return False

    def getbranches(self, project_id):
        """
        List all the branches from a project

        :param project_id: project id
        :return: the branches
        """
        request = requests.get(
            '{0}/{1}/repository/branches'.format(self.projects_url, project_id),
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def getbranch(self, project_id, branch):
        """
        List one branch from a project

        :param project_id: project id
        :param branch: branch id
        :return: the branch
        """
        request = requests.get(
            '{0}/{1}/repository/branches/{2}'.format(self.projects_url, project_id, branch),
            headers=self.headers, verify=self.verify_ssl,
            auth=self.auth, timeout=self.timeout
        )

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def createbranch(self, project_id, branch, ref):
        """
        Create branch from commit SHA or existing branch

        :param project_id:  The ID of a project
        :param branch: The name of the branch
        :param ref: Create branch from commit SHA or existing branch
        :return: True if success, False if not
        """
        data = {"id": project_id, "branch_name": branch, "ref": ref}

        request = requests.post(
            '{0}/{1}/repository/branches'.format(self.projects_url, project_id),
            headers=self.headers, data=data, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 201:
            return request.json()
        else:
            return False

    def deletebranch(self, project_id, branch):
        """
        Delete branch by name

        :param project_id:  The ID of a project
        :param branch: The name of the branch
        :return: True if success, False if not
        """

        request = requests.delete(
            '{0}/{1}/repository/branches/{2}'.format(self.projects_url, project_id, branch),
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return True
        else:
            return False

    def protectbranch(self, project_id, branch):
        """
        Protect a branch from changes

        :param project_id: project id
        :param branch: branch id
        :return: True if success
        """
        request = requests.put(
            '{0}/{1}/repository/branches/{2}/protect'.format(self.projects_url, project_id, branch),
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return True
        else:
            return False

    def unprotectbranch(self, project_id, branch):
        """
        Stop protecting a branch

        :param project_id: project id
        :param branch: branch id
        :return: true if success
        """
        request = requests.put(
            '{0}/{1}/repository/branches/{2}/unprotect'.format(self.projects_url, project_id, branch),
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return True
        else:
            return False

    def createforkrelation(self, project_id, from_project_id):
        """
        Create a fork relation.

        This DO NOT create a fork but only adds a link as fork the relation between 2 repositories

        :param project_id: project id
        :param from_project_id: from id
        :return: true if success
        """
        data = {'id': project_id, 'forked_from_id': from_project_id}

        request = requests.post(
            '{0}/{1}/fork/{2}'.format(self.projects_url, project_id, from_project_id),
            headers=self.headers, data=data, verify=self.verify_ssl,
            auth=self.auth, timeout=self.timeout)

        if request.status_code == 201:
            return True
        else:
            return False

    def removeforkrelation(self, project_id):
        """
        Remove an existing fork relation. this DO NOT remove the fork,only the relation between them

        :param project_id: project id
        :return: true if success
        """
        request = requests.delete(
            '{0}/{1}/fork'.format(self.projects_url, project_id),
            headers=self.headers, verify=self.verify_ssl,
            auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return True
        else:
            return False

    def createfork(self, project_id):
        """
        Forks a project into the user namespace of the authenticated user.

        :param project_id: Project ID to fork
        :return: True if succeed
        """

        request = requests.post(
            '{0}/fork/{1}'.format(self.projects_url, project_id),
            timeout=self.timeout, verify=self.verify_ssl)

        if request.status_code == 200:
            return True
        else:
            return False

    def getissues(self, page=1, per_page=20):
        """
        Return a global list of issues for your user.

        :param page: Page number
        :param per_page: Records per page
        :return: list of issues
        """
        data = {'page': page, 'per_page': per_page}

        request = requests.get(
            '{0}/api/v3/issues'.format(self.host),
            params=data, headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def getprojectissues(self, project_id, page=1, per_page=20, **kwargs):
        """
        Return a list of issues for project id.

        :param: project_id: The id for the project.
        :param page: Page number
        :param per_page: Records per page
        :param kwargs: Extra data to send
        :return: list of issues
        """
        kwargs['page'] = page
        kwargs['per_page'] = per_page
        data = kwargs

        request = requests.get(
            '{0}/{1}/issues'.format(self.projects_url, project_id),
            params=data, headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def getprojectissue(self, project_id, issue_id):
        """
        Get an specific issue id from a project

        :param project_id: project id
        :param issue_id: issue id
        :return: the issue
        """
        request = requests.get(
            '{0}/{1}/issues/{2}'.format(self.projects_url, project_id, issue_id),
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def createissue(self, project_id, title, **kwargs):
        """
        Create a new issue

        :param project_id: project id
        :param title: title of the issue
        :return: dict with the issue created
        """
        data = {'id': id, 'title': title}
        if kwargs:
            data.update(kwargs)
        request = requests.post(
            '{0}/{1}/issues'.format(self.projects_url, project_id),
            headers=self.headers, data=data, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 201:
            return request.json()
        else:
            return False

    def editissue(self, project_id, issue_id, **kwargs):
        """
        Edit an existing issue data

        :param project_id: project id
        :param issue_id: issue id
        :return: true if success
        """
        data = {'id': project_id, 'issue_id': issue_id}
        if kwargs:
            data.update(kwargs)
        request = requests.put(
            '{0}/{1}/issues/{2}'.format(self.projects_url, project_id, issue_id),
            headers=self.headers, data=data, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def getmilestones(self, project_id, page=1, per_page=20):
        """
        Get the milestones for a project

        :param project_id: project id
        :param page: Page number
        :param per_page: Records per page
        :return: the milestones
        """
        data = {'page': page, 'per_page': per_page}

        request = requests.get(
            '{0}/{1}/milestones'.format(self.projects_url, project_id), params=data,
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def getmilestone(self, project_id, milestone_id):
        """
        Get an specific milestone

        :param project_id: project id
        :param milestone_id: milestone id
        :return: dict with the new milestone
        """
        request = requests.get(
            '{0}/{1}/milestones/{2}'.format(self.projects_url, project_id, milestone_id),
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def createmilestone(self, project_id, title, **kwargs):
        """
        Create a new milestone

        :param project_id: project id
        :param title: title
        :param description: description
        :param due_date: due date
        :param sudo: do the request as another user
        :return: dict of the new issue
        """
        data = {'id': project_id, 'title': title}

        if kwargs:
            data.update(kwargs)

        request = requests.post(
            '{0}/{1}/milestones'.format(self.projects_url, project_id),
            headers=self.headers, data=data, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 201:
            return request.json()
        else:
            return False

    def editmilestone(self, project_id, milestone_id, **kwargs):
        """Edit an existing milestone

        :param project_id: project id
        :param milestone_id: milestone id
        :param title: title
        :param description: description
        :param due_date: due date
        :param state_event: state
        :param sudo: do the request as another user
        :return: dict with the modified milestone
        """
        data = {'id': project_id, 'milestone_id': milestone_id}

        if kwargs:
            data.update(kwargs)

        request = requests.put(
            '{0}/{1}/milestones/{2}'.format(self.projects_url, project_id, milestone_id),
            headers=self.headers, data=data, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def getmilestoneissues(self, project_id, milestone_id, page=1, per_page=20):
        """
        Get the issues associated with a milestone

        :param project_id: project id
        :param milestone_id: milestone id
        :return: list of issues
        """
        data = {'page': page, 'per_page': per_page}

        request = requests.get(
            '{0}/{1}/milestones/{2}/issues'.format(self.projects_url, project_id, milestone_id),
            params=data, headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def get_all_deploy_keys(self):
        """
        Get a list of all deploy keys across all projects of the GitLab instance.
        This endpoint requires admin access.

        >>> gitlab = Gitlab(host='http://localhost:10080', verify_ssl=False)
        >>> gitlab.login(user='root', password='5iveL!fe')
        >>> gitlab.get_all_deploy_keys()

        :return: List of Dictionaries containing all deploy keys
        :raise: HttpError: If invalid response returned
        """
        return self.get('/deploy_keys', default_response=[])

    def enable_deploy_key(self, project, key_id):
        """
        Enables a deploy key for a project.

        >>> gitlab = Gitlab(host='http://localhost:10080', verify_ssl=False)
        >>> gitlab.login(user='root', password='5iveL!fe')
        >>> gitlab.enable_deploy_key(15, 5)

        :param project: The ID or URL-encoded path of the project owned by the authenticated user
        :param key_id: The ID of the deploy key
        :return: A dictionary containing deploy key details
        :raise: HttpError: If invalid response returned
        """
        url = '/projects/{project}/deploy_keys/{key_id}/enable'.format(
            project=project, key_id=key_id)
        return self.post(url, default_response={})

    def getdeploykeys(self, project_id):
        """
        Get a list of a project's deploy keys.

        :param project_id: project id
        :return: the keys in a dictionary if success, false if not
        """
        request = requests.get(
            '{0}/{1}/keys'.format(self.projects_url, project_id),
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout
        )

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def getdeploykey(self, project_id, key_id):
        """
        Get a single key.

        :param project_id: project id
        :param key_id: key id
        :return: the key in a dict if success, false if not
        """
        request = requests.get(
            '{0}/{1}/keys/{2}'.format(self.projects_url, project_id, key_id),
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def adddeploykey(self, project_id, title, key):
        """
        Creates a new deploy key for a project.

        :param project_id: project id
        :param title: title of the key
        :param key: the key itself
        :return: true if success, false if not
        """
        data = {'id': project_id, 'title': title, 'key': key}

        request = requests.post(
            '{0}/{1}/keys'.format(self.projects_url, project_id),
            headers=self.headers, data=data, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 201:
            return request.json()
        else:
            return False

    def deletedeploykey(self, project_id, key_id):
        """
        Delete a deploy key from a project

        :param project_id: project id
        :param key_id: key id to delete
        :return: true if success, false if not
        """
        request = requests.delete(
            '{0}/{1}/keys/{2}'.format(self.projects_url, project_id, key_id),
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return True
        else:
            return False

    def creategroup(self, name, path, **kwargs):
        """
        Creates a new group

        :param name: The name of the group
        :param path: The path for the group
        :param kwargs: Any param the the Gitlab API supports
        :return: dict of the new group
        """
        data = {'name': name, 'path': path}

        if kwargs:
            data.update(kwargs)

        request = requests.post(
            self.groups_url, data=data, headers=self.headers,
            verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 201:
            return request.json()
        else:
            msg = request.json()['message']
            raise exceptions.HttpError(msg)

    def getgroups(self, group_id=None, page=1, per_page=20):
        """
        Retrieve group information

        :param group_id: Specify a group. Otherwise, all groups are returned
        :param page: Page Number
        :param per_page: Records Per Page
        :return: list of groups
        """
        data = {'page': page, 'per_page': per_page}

        request = requests.get(
            '{0}/{1}'.format(self.groups_url, group_id if group_id else ''),
            params=data, headers=self.headers, timeout=self.timeout, verify=self.verify_ssl, auth=self.auth)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def moveproject(self, group_id, project_id):
        """
        Move a given project into a given group

        :param group_id: ID of the destination group
        :param project_id: ID of the project to be moved
        :return: dict of the updated project
        """
        request = requests.post(
            '{0}/{1}/projects/{2}'.format(self.groups_url, group_id, project_id),
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 201:
            return request.json()
        else:
            return False

    def getmergerequests(self, project_id, page=1, per_page=20, state=None):
        """
        Get all the merge requests for a project.

        :param project_id: ID of the project to retrieve merge requests for
        :param page: Page Number
        :param per_page: Records per page
        :param state: Passes merge request state to filter them by it
        :return: list with all the merge requests
        """
        data = {'page': page, 'per_page': per_page, 'state': state}

        request = requests.get(
            '{0}/{1}/merge_requests'.format(self.projects_url, project_id),
            params=data, headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def getmergerequest(self, project_id, mergerequest_id):
        """
        Get information about a specific merge request.

        :param project_id: ID of the project
        :param mergerequest_id: ID of the merge request
        :return: dict of the merge request
        """
        request = requests.get(
            '{0}/{1}/merge_request/{2}'.format(self.projects_url, project_id, mergerequest_id),
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def getmergerequestcomments(self, project_id, mergerequest_id, page=1, per_page=20):
        """
        Get comments of a merge request.

        :param project_id: ID of the project
        :param mergerequest_id: ID of the merge request
        :param page: Page number
        :param per_page: Records per page
        :return: list of the comments
        """
        data = {'page': page, 'per_page': per_page}

        request = requests.get(
            '{0}/{1}/merge_request/{2}/comments'.format(self.projects_url, project_id, mergerequest_id),
            params=data, headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def getmergerequestchanges(self, project_id, mergerequest_id):
        """
        Get changes of a merge request.

        :param project_id: ID of the project
        :param mergerequest_id: ID of the merge request
        :return: information about the merge request including files and changes
        """
        request = requests.get(
            '{0}/{1}/merge_request/{2}/changes'.format(self.projects_url, project_id, mergerequest_id),
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def createmergerequest(self, project_id, sourcebranch, targetbranch,
                           title, target_project_id=None, assignee_id=None):
        """
        Create a new merge request.

        :param project_id: ID of the project originating the merge request
        :param sourcebranch: name of the branch to merge from
        :param targetbranch: name of the branch to merge to
        :param title: Title of the merge request
        :param assignee_id: Assignee user ID
        :return: dict of the new merge request
        """
        data = {
            'source_branch': sourcebranch,
            'target_branch': targetbranch,
            'title': title,
            'assignee_id': assignee_id,
            'target_project_id': target_project_id
        }

        request = requests.post(
            '{0}/{1}/merge_requests'.format(self.projects_url, project_id),
            data=data, headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 201:
            return request.json()
        else:
            return False

    def updatemergerequest(self, project_id, mergerequest_id, **kwargs):
        """
        Update an existing merge request.

        :param project_id: ID of the project originating the merge request
        :param mergerequest_id: ID of the merge request to update
        :param sourcebranch: name of the branch to merge from
        :param targetbranch: name of the branch to merge to
        :param title: Title of the merge request
        :param assignee_id: Assignee user ID
        :param closed: MR status.  True = closed
        :return: dict of the modified merge request
        """
        data = {}

        if kwargs:
            data.update(kwargs)

        request = requests.put(
            '{0}/{1}/merge_request/{2}'.format(self.projects_url, project_id, mergerequest_id),
            data=data, headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def acceptmergerequest(self, project_id, mergerequest_id, merge_commit_message=None):
        """
        Update an existing merge request.

        :param project_id: ID of the project originating the merge request
        :param mergerequest_id: ID of the merge request to accept
        :param merge_commit_message: Custom merge commit message
        :return: dict of the modified merge request
        """

        data = {'merge_commit_message': merge_commit_message}

        request = requests.put(
            '{0}/{1}/merge_request/{2}/merge'.format(self.projects_url, project_id, mergerequest_id),
            data=data, headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def addcommenttomergerequest(self, project_id, mergerequest_id, note):
        """
        Add a comment to a merge request.

        :param project_id: ID of the project originating the merge request
        :param mergerequest_id: ID of the merge request to comment on
        :param note: Text of comment
        :return: True if success
        """
        request = requests.post(
            '{0}/{1}/merge_request/{2}/comments'.format(self.projects_url, project_id, mergerequest_id),
            data={'note': note}, headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        return request.status_code == 201

    def getsnippets(self, project_id, page=1, per_page=20):
        """
        Get all the snippets of the project identified by project_id

        :param project_id: project id to get the snippets from
        :return: list of dictionaries
        """
        data = {'page': page, 'per_page': per_page}

        request = requests.get(
            '{0}/{1}/snippets'.format(self.projects_url, project_id), params=data,
            verify=self.verify_ssl, auth=self.auth, headers=self.headers, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def getsnippet(self, project_id, snippet_id):
        """
        Get one snippet from a project

        :param project_id: project id to get the snippet from
        :param snippet_id: snippet id
        :return: dictionary
        """
        request = requests.get(
            '{0}/{1}/snippets/{2}'.format(self.projects_url, project_id, snippet_id),
            verify=self.verify_ssl, auth=self.auth, headers=self.headers, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def createsnippet(self, project_id, title, file_name, code, visibility_level=0):
        """
        Creates an snippet

        :param project_id: project id to create the snippet under
        :param title: title of the snippet
        :param file_name: filename for the snippet
        :param code: content of the snippet
        :param visibility_level: snippets can be either private (0), internal(10) or public(20)
        :return: True if correct, false if failed
        """
        data = {'id': project_id, 'title': title, 'file_name': file_name, 'code': code}

        if visibility_level in [0, 10, 20]:
            data['visibility_level'] = visibility_level

        request = requests.post(
            '{0}/{1}/snippets'.format(self.projects_url, project_id),
            data=data, verify=self.verify_ssl, auth=self.auth, headers=self.headers, timeout=self.timeout)

        if request.status_code == 201:
            return request.json()
        else:
            return False

    def getsnippetcontent(self, project_id, snippet_id):
        """
        Get raw content of a given snippet

        :param project_id: project_id for the snippet
        :param snippet_id: snippet id
        :return: the content of the snippet
        """
        request = requests.get(
            '{0}/{1}/snippets/{2}/raw'.format(self.projects_url, project_id, snippet_id),
            verify=self.verify_ssl, auth=self.auth, headers=self.headers, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def deletesnippet(self, project_id, snippet_id):
        """Deletes a given snippet

        :param project_id: project_id
        :param snippet_id: snippet id
        :return: True if success
        """
        request = requests.delete(
            '{0}/{1}/snippets/{2}'.format(self.projects_url, project_id, snippet_id),
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        return request.status_code == 200

    def getrepositories(self, project_id, page=1, per_page=20):
        """
        Gets all repositories for a project id

        :param project_id: project id
        :param page: Page number
        :param per_page: Records per page
        :return: list of repos
        """
        data = {'page': page, 'per_page': per_page}

        request = requests.get(
            '{0}/{1}/repository/branches'.format(self.projects_url, project_id), params=data,
            verify=self.verify_ssl, auth=self.auth, headers=self.headers, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def getrepositorybranch(self, project_id, branch):
        """
        Get a single project repository branch.

        :param project_id: project id
        :param branch: branch
        :return: dict of the branch
        """
        request = requests.get(
            '{0}/{1}/repository/branches/{2}'.format(self.projects_url, project_id, branch),
            verify=self.verify_ssl, auth=self.auth, headers=self.headers, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        elif request.status_code == 404:
            if request.json()['message'] == "404 Branch does not exist Not Found":
                # In the future we should raise an exception here
                return False
        else:
            return False

    def protectrepositorybranch(self, project_id, branch):
        """
        Protects a single project repository branch. This is an idempotent function,
        protecting an already protected repository branch still returns a 200 OK status code.

        :param project_id: project id
        :param branch: branch to protect
        :return: dict with the branch
        """
        request = requests.put(
            '{0}/{1}/repository/branches/{2}/protect'.format(self.projects_url, project_id, branch),
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def unprotectrepositorybranch(self, project_id, branch):
        """
        Unprotects a single project repository branch. This is an idempotent function,
        unprotecting an already unprotected repository branch still returns a 200 OK status code.

        :param project_id: project id
        :param branch: branch to unprotect
        :return: dict with the branch
        """
        request = requests.put(
            '{0}/{1}/repository/branches/{2}/unprotect'.format(self.projects_url, project_id, branch),
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return

    def getrepositorytags(self, project_id, page=1, per_page=20):
        """
        Get a list of repository tags from a project, sorted by name in reverse alphabetical order.

        :param project_id: project id
        :param page: Page number
        :param per_page: Records per page
        :return: list with all the tags
        """
        data = {'page': page, 'per_page': per_page}
        request = requests.get(
            '{0}/{1}/repository/tags'.format(self.projects_url, project_id), params=data,
            verify=self.verify_ssl, auth=self.auth, headers=self.headers, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def createrepositorytag(self, project_id, tag_name, ref, message=None):
        """
        Creates new tag in the repository that points to the supplied ref

        :param project_id: project id
        :param tag_name: tag
        :param ref: sha1 of the commit or branch to tag
        :param message: message
        :return: dict
        """

        data = {'id': project_id, 'tag_name': tag_name, 'ref': ref, 'message': message}
        request = requests.post(
            '{0}/{1}/repository/tags'.format(self.projects_url, project_id), data=data,
            verify=self.verify_ssl, auth=self.auth, headers=self.headers, timeout=self.timeout)

        if request.status_code == 201:
            return request.json()
        else:
            return False

    def delete_repository_tag(self, project_id, tag_name):
        """
        Deletes a tag of a repository with given name.

        :param project_id: The ID of a project
        :param tag_name: The name of a tag
        :return: Dictionary containing delete tag
        :raise: HttpError: If invalid response returned
        """
        return self.delete('/projects/{project_id}/repository/tags/{tag_name}'.format(
            project_id=project_id, tag_name=tag_name))

    def addcommenttocommit(self, project_id, author, sha, path, line, note):
        """
        Adds an inline comment to a specific commit

        :param project_id: project id
        :param author: The author info as returned by create mergerequest
        :param sha: The name of a repository branch or tag or if not given the default branch
        :param path: The file path
        :param line: The line number
        :param note: Text of comment
        :return: True or False
        """

        data = {
            'author': author,
            'note': note,
            'path': path,
            'line': line,
            'line_type': 'new'
        }

        request = requests.post(
            '{0}/{1}/repository/commits/{2}/comments'.format(self.projects_url, project_id, sha),
            headers=self.headers, data=data, verify=self.verify_ssl)

        if request.status_code == 201:
            return True
        else:
            return False

    def getrepositorycommits(self, project_id, ref_name=None, page=1, per_page=20):
        """
        Get a list of repository commits in a project.

        :param project_id: The ID of a project
        :param ref_name: The name of a repository branch or tag or if not given the default branch
        :param page: Page number
        :param per_page: Records per page
        :return: list of commits
        """
        data = {'page': page, 'per_page': per_page}

        if ref_name is not None:
            data.update({'ref_name': ref_name})

        request = requests.get(
            '{0}/{1}/repository/commits'.format(self.projects_url, project_id),
            verify=self.verify_ssl, auth=self.auth, params=data,
            headers=self.headers, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def getrepositorycommit(self, project_id, sha1):
        """
        Get a specific commit identified by the commit hash or name of a branch or tag.

        :param project_id: The ID of a project
        :param sha1: The commit hash or name of a repository branch or tag
        :return: dict of commit
        """
        request = requests.get(
            '{0}/{1}/repository/commits/{2}'.format(self.projects_url, project_id, sha1),
            verify=self.verify_ssl, auth=self.auth, headers=self.headers, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def getrepositorycommitdiff(self, project_id, sha1):
        """
        Get the diff of a commit in a project

        :param project_id: The ID of a project
        :param sha1: The name of a repository branch or tag or if not given the default branch
        :return: dict with the diff
        """
        request = requests.get(
            '{0}/{1}/repository/commits/{2}/diff'.format(self.projects_url, project_id, sha1),
            verify=self.verify_ssl, auth=self.auth, headers=self.headers, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def getrepositorytree(self, project_id, **kwargs):
        """
        Get a list of repository files and directories in a project.

        :param project_id: The ID of a project
        :param path: The path inside repository. Used to get contend of subdirectories
        :param ref_name: The name of a repository branch or tag or if not given the default branch
        :return: dict with the tree
        """
        data = {}

        if kwargs:
            data.update(kwargs)

        request = requests.get(
            '{0}/{1}/repository/tree'.format(self.projects_url, project_id), params=data,
            verify=self.verify_ssl, auth=self.auth, headers=self.headers, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def getrawfile(self, project_id, sha1, filepath):
        """
        Get the raw file contents for a file by commit SHA and path.

        :param project_id: The ID of a project
        :param sha1: The commit or branch name
        :param filepath: The path the file
        :return: raw file contents
        """
        data = {'filepath': filepath}

        request = requests.get(
            '{0}/{1}/repository/blobs/{2}'.format(self.projects_url, project_id, sha1),
            params=data, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout,
            headers=self.headers)

        if request.status_code == 200:
            return request.content
        else:
            return False

    def getrawblob(self, project_id, sha1):
        """
        Get the raw file contents for a blob by blob SHA.

        :param project_id: The ID of a project
        :param sha1: the commit sha
        :return: raw blob
        """
        request = requests.get(
            '{0}/{1}/repository/raw_blobs/{2}'.format(self.projects_url, project_id, sha1),
            verify=self.verify_ssl, auth=self.auth, headers=self.headers, timeout=self.timeout)

        if request.status_code == 200:
            return request.content
        else:
            return False

    def getcontributors(self, project_id, page=1, per_page=20):
        """
        Get repository contributors list

        :param project_id: The ID of a project
        :param page: Page number
        :param per_page: Records per page
        :return: list of contributors or False
        """
        data = {'page': page, 'per_page': per_page}

        request = requests.get(
            '{0}/{1}/repository/contributors'.format(self.projects_url, project_id), params=data,
            verify=self.verify_ssl, auth=self.auth, headers=self.headers, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def compare_branches_tags_commits(self, project_id, from_id, to_id):
        """
        Compare branches, tags or commits

        :param project_id: The ID of a project
        :param from_id: the commit sha or branch name
        :param to_id: the commit sha or branch name
        :return: commit list and diff between two branches tags or commits provided by name
        :raise: HttpError: If invalid response returned
        """
        data = {'from': from_id, 'to': to_id}

        request = requests.get(
            '{0}/{1}/repository/compare'.format(self.projects_url, project_id),
            params=data, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout,
            headers=self.headers)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def searchproject(self, search, page=1, per_page=20):
        """
        Search for projects by name which are accessible to the authenticated user

        :param search: Query to search for
        :param page: Page number
        :param per_page: Records per page
        :return: list of results
        """
        data = {'page': page, 'per_page': per_page}
        request = requests.get("{0}/{1}".format(self.search_url, search), params=data,
                               verify=self.verify_ssl, auth=self.auth, headers=self.headers, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def getfilearchive(self, project_id, filepath=None):
        """
        Get an archive of the repository

        :param project_id: project id
        :param filepath: path to save the file to
        :return: True if the file was saved to the filepath
        """
        if not filepath:
            filepath = ''

        request = requests.get(
            '{0}/{1}/repository/archive'.format(self.projects_url, project_id),
            verify=self.verify_ssl, auth=self.auth, headers=self.headers, timeout=self.timeout)

        if request.status_code == 200:
            if filepath == "":
                filepath = request.headers['content-disposition'].split(';')[1].split('=')[1].strip('"')
            with open(filepath, 'wb') as filesave:
                filesave.write(request.content)
                # TODO: Catch oserror exceptions as no permissions and such
                # TODO: change the filepath to a path and keep always the filename?
            return True
        else:
            msg = request.json()['message']
            raise exceptions.HttpError(msg)

    def deletegroup(self, group_id):
        """
        Deletes an group by ID

        :param group_id: id of the group to delete
        :return: True if it deleted, False if it couldn't. False could happen for several reasons, but there isn't a good way of differentiating them
        """
        request = requests.delete(
            '{0}/{1}'.format(self.groups_url, group_id),
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        return request.status_code == 200

    def getgroupmembers(self, group_id, page=1, per_page=20):
        """
        Lists the members of a given group id

        :param group_id: the group id
        :param page: which page to return (default is 1)
        :param per_page: number of items to return per page (default is 20)
        :return: the group's members
        """
        data = {'page': page, 'per_page': per_page}

        request = requests.get(
            '{0}/{1}/members'.format(self.groups_url, group_id), params=data,
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def addgroupmember(self, group_id, user_id, access_level):
        """
        Adds a project member to a project

        :param user_id: user id
        :param access_level: access level, see gitlab help to know more
        :return: True if success
        """
        if not isinstance(access_level, int):
            if access_level.lower() == 'owner':
                access_level = 50
            elif access_level.lower() == 'master':
                access_level = 40
            elif access_level.lower() == 'developer':
                access_level = 30
            elif access_level.lower() == 'reporter':
                access_level = 20
            elif access_level.lower() == 'guest':
                access_level = 10
            else:
                return False

        data = {'id': group_id, 'user_id': user_id, 'access_level': access_level}

        request = requests.post(
            '{0}/{1}/members'.format(self.groups_url, group_id),
            headers=self.headers, data=data, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        return request.status_code == 201

    def editgroupmember(self, group_id, user_id, access_level):
        """
        Edit user access level in a group

        :param group_id: group id
        :param user_id: user id
        :param access_level: access level, see gitlab help to know more
        :return: True if success
        """
        if not isinstance(access_level, int):
            if access_level.lower() == 'owner':
                access_level = 50
            elif access_level.lower() == 'master':
                access_level = 40
            elif access_level.lower() == 'developer':
                access_level = 30
            elif access_level.lower() == 'reporter':
                access_level = 20
            elif access_level.lower() == 'guest':
                access_level = 10
            else:
                return False

        data = {'id': group_id, 'user_id': user_id, 'access_level': access_level}

        request = requests.put(
            '{0}/{1}/members/{2}'.format(self.groups_url, group_id, user_id),
            headers=self.headers, data=data, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        return request.status_code == 200

    def deletegroupmember(self, group_id, user_id):
        """
        Delete a group member

        :param group_id: group id to remove the member from
        :param user_id: user id
        :return: always true
        """
        request = requests.delete(
            '{0}/{1}/members/{2}'.format(self.groups_url, group_id, user_id),
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return True  # It always returns true

    def addldapgrouplink(self, group_id, cn, group_access, provider):
        """
        Add LDAP group link

        :param id: The ID of a group
        :param cn: The CN of a LDAP group
        :param group_access: Minimum access level for members of the LDAP group
        :param provider: LDAP provider for the LDAP group (when using several providers)
        :return: True if success
        """
        data = {'id': group_id, 'cn': cn, 'group_access': group_access, 'provider': provider}

        request = requests.post(
            '{0}/{1}/ldap_group_links'.format(self.groups_url, group_id),
            headers=self.headers, data=data, verify=self.verify_ssl)

        return request.status_code == 201

    def deleteldapgrouplink(self, group_id, cn, provider=None):
        """
        Deletes a LDAP group link (for a specific LDAP provider if given)

        :param group_id: The ID of a group
        :param cn: The CN of a LDAP group
        :param provider: Name of a LDAP provider
        :return: True if success
        """
        url = '{base}/{gid}/ldap_group_links/{provider}{cn}'.format(
            base=self.groups_url, gid=group_id, cn=cn,
            provider=('{0}/'.format(provider) if provider else ''))

        request = requests.delete(url, headers=self.headers, verify=self.verify_ssl)

        return request.status_code == 200

    def getissuewallnotes(self, project_id, issue_id, page=1, per_page=20):
        """
        Get the notes from the wall of a issue

        :param project_id: Project ID
        :param issue_id: Issue ID
        :param page: Page Number
        :param per_page: Records per page
        """
        data = {'page': page, 'per_page': per_page}

        request = requests.get(
            '{0}/{1}/issues/{2}/notes'.format(self.projects_url, project_id, issue_id), params=data,
            verify=self.verify_ssl, auth=self.auth, headers=self.headers, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def getissuewallnote(self, project_id, issue_id, note_id):
        """
        Get one note from the wall of the issue

        :param project_id: Project ID
        :param issue_id: Issue ID
        :param note_id: Note ID
        :return: Json or False
        """
        request = requests.get(
            '{0}/{1}/issues/{2}/notes/{3}'.format(self.projects_url, project_id, issue_id, note_id),
            verify=self.verify_ssl, auth=self.auth, headers=self.headers, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def createissuewallnote(self, project_id, issue_id, content):
        """Create a new note

        :param project_id: Project ID
        :param issue_id:  Issue ID
        :param content: Contents
        :return: Json or False
        """
        data = {'body': content}
        request = requests.post(
            '{0}/{1}/issues/{2}/notes'.format(self.projects_url, project_id, issue_id),
            verify=self.verify_ssl, auth=self.auth, headers=self.headers, data=data, timeout=self.timeout)

        if request.status_code == 201:
            return request.json()
        else:
            return False

    def getsnippetwallnotes(self, project_id, snippet_id, page=1, per_page=20):
        """
        Get the notes from the wall of a snippet

        :param project_id: Project ID
        :param snippet_id: Snippet ID
        :param page: Page number
        :param per_page: Records per page
        :return: Json or False
        """
        data = {'page': page, 'per_page': per_page}
        request = requests.get(
            '{0}/{1}/snippets/{2}/notes'.format(self.projects_url, project_id, snippet_id),
            params=data, verify=self.verify_ssl, auth=self.auth, headers=self.headers, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def getsnippetwallnote(self, project_id, snippet_id, note_id):
        """
        Get one note from the wall of the snippet

        :param project_id: Project ID
        :param snippet_id: Snippet ID
        :param note_id: Note ID
        :return: Json or False
        """
        request = requests.get(
            '{0}/{1}/snippets/{2}/notes/{3}'.format(self.projects_url, project_id, snippet_id, note_id),
            verify=self.verify_ssl, auth=self.auth, headers=self.headers, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def createsnippetewallnote(self, project_id, snippet_id, content):
        """
        Create a new note

        :param project_id: Project ID
        :param snippet_id: Snippet ID
        :param content: Content
        :return: Json or False
        """
        data = {'body': content}

        request = requests.post(
            '{0}/{1}/snippets/{2}/notes'.format(self.projects_url, project_id, snippet_id),
            verify=self.verify_ssl, auth=self.auth, headers=self.headers, data=data, timeout=self.timeout)

        if request.status_code == 201:
            return request.json()
        else:
            return False

    def getmergerequestwallnotes(self, project_id, merge_request_id, page=1, per_page=20):
        """
        Get the notes from the wall of a merge request

        :param project_id: Project ID
        :param merge_request_id: Merger Request ID
        :param page: Page number
        :param per_page: Records per page
        :return: Json or False
        """
        data = {'page': page, 'per_page': per_page}

        request = requests.get(
            '{0}/{1}/merge_requests/{2}/notes'.format(self.projects_url, project_id, merge_request_id),
            params=data, verify=self.verify_ssl, auth=self.auth, headers=self.headers, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def getmergerequestwallnote(self, project_id, merge_request_id, note_id):
        """
        Get one note from the wall of the merge request

        :param project_id: Project ID
        :param merge_request_id: Merger Request ID
        :param note_id: Note ID
        :return: Json or False
        """
        request = requests.get(
            '{0}/{1}/merge_requests/{2}/notes/{3}'.format(self.projects_url, project_id, merge_request_id, note_id),
            verify=self.verify_ssl, auth=self.auth, headers=self.headers, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def createmergerequestewallnote(self, project_id, merge_request_id, content):
        """
        Create a new note

        :param project_id: Project ID
        :param merge_request_id: Merger Request ID
        :param content: Content
        :return: Json or False
        """
        data = {'body': content}

        request = requests.post(
            '{0}/{1}/merge_requests/{2}/notes'.format(self.projects_url, project_id, merge_request_id),
            verify=self.verify_ssl, auth=self.auth, headers=self.headers, data=data, timeout=self.timeout)

        if request.status_code == 201:
            return request.json()
        else:
            return False

    def createfile(self, project_id, file_path, branch_name, encoding, content, commit_message):
        """
        Creates a new file in the repository

        :param project_id: project id
        :param file_path: Full path to new file. Ex. lib/class.rb
        :param branch_name: The name of branch
        :param content: File content
        :param commit_message: Commit message
        :return: true if success, false if not
        """
        data = {
            'file_path': file_path,
            'branch_name': branch_name,
            'encoding': encoding,
            'content': content,
            'commit_message': commit_message
        }

        request = requests.post(
            '{0}/{1}/repository/files'.format(self.projects_url, project_id),
            verify=self.verify_ssl, auth=self.auth, headers=self.headers, data=data, timeout=self.timeout)

        return request.status_code == 201

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
        data = {
            'file_path': file_path,
            'branch_name': branch_name,
            'content': content,
            'commit_message': commit_message
        }

        request = requests.put(
            '{0}/{1}/repository/files'.format(self.projects_url, project_id),
            headers=self.headers, data=data, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        return request.status_code == 200

    def getfile(self, project_id, file_path, ref):
        """
        Allows you to receive information about file in repository like name, size, content.
        Note that file content is Base64 encoded.

        :param project_id: project_id
        :param file_path: Full path to file. Ex. lib/class.rb
        :param ref: The name of branch, tag or commit
        :return:
        """
        data = {'file_path': file_path, 'ref': ref}

        request = requests.get(
            '{0}/{1}/repository/files'.format(self.projects_url, project_id),
            headers=self.headers, data=data, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
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
        data = {
            'file_path': file_path,
            'branch_name': branch_name,
            'commit_message': commit_message
        }

        request = requests.delete(
            '{0}/{1}/repository/files'.format(self.projects_url, project_id),
            headers=self.headers, data=data, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        return request.status_code == 200

    def setgitlabciservice(self, project_id, token, project_url):
        """
        Set GitLab CI service for project

        :param project_id: project id
        :param token: CI project token
        :param project_url: CI project url
        :return: true if success, false if not
        """
        data = {'token': token, 'project_url': project_url}

        request = requests.put(
            '{0}/{1}/services/gitlab-ci'.format(self.projects_url, project_id),
            verify=self.verify_ssl, auth=self.auth, headers=self.headers, data=data, timeout=self.timeout)

        return request.status_code == 200

    def deletegitlabciservice(self, project_id, token, project_url):
        """
        Delete GitLab CI service settings

        :param project_id: Project ID
        :param token: Token
        :param project_url: Project URL
        :return: true if success, false if not
        """
        request = requests.delete(
            '{0}/{1}/services/gitlab-ci'.format(self.projects_url, project_id),
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        return request.status_code == 200

    def getlabels(self, project_id):
        """
        Get all labels for given project.

        :param project_id: The ID of a project
        :return: list of the labels
        """
        request = requests.get(
            '{0}/{1}/labels'.format(self.projects_url, project_id),
            verify=self.verify_ssl, auth=self.auth, headers=self.headers, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def createlabel(self, project_id, name, color):
        """
        Creates a new label for given repository with given name and color.

        :param project_id: The ID of a project
        :param name: The name of the label
        :param color: Color of the label given in 6-digit hex notation with leading '#' sign (e.g. #FFAABB)
        :return:
        """
        data = {'name': name, 'color': color}

        request = requests.post(
            '{0}/{1}/labels'.format(self.projects_url, project_id), data=data,
            verify=self.verify_ssl, auth=self.auth, headers=self.headers, timeout=self.timeout)

        if request.status_code == 201:
            return request.json()
        else:
            return False

    def deletelabel(self, project_id, name):
        """
        Deletes a label given by its name.

        :param project_id: The ID of a project
        :param name: The name of the label
        :return: True if succeed
        """
        data = {'name': name}

        request = requests.delete(
            '{0}/{1}/labels'.format(self.projects_url, project_id), data=data,
            verify=self.verify_ssl, auth=self.auth, headers=self.headers, timeout=self.timeout)

        return request.status_code == 200

    def editlabel(self, project_id, name, new_name=None, color=None):
        """
        Updates an existing label with new name or now color.
        At least one parameter is required, to update the label.

        :param project_id: The ID of a project
        :param name: The name of the label
        :return: True if succeed
        """
        data = {'name': name, 'new_name': new_name, 'color': color}

        request = requests.put(
            '{0}/{1}/labels'.format(self.projects_url, project_id), data=data,
            verify=self.verify_ssl, auth=self.auth, headers=self.headers, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def getnamespaces(self, search=None, page=1, per_page=20):
        """
        Return a namespace list

        :param search: Optional search query
        :param page: Which page to return (default is 1)
        :param per_page: Number of items to return per page (default is 20)
        :return: returns a list of namespaces, false if there is an error
        """
        data = {'page': page, 'per_page': per_page}

        if search:
            data['search'] = search

        request = requests.get(
            self.namespaces_url, params=data, headers=self.headers, verify=self.verify_ssl)

        if request.status_code == 200:
            return request.json()
        else:
            return False
