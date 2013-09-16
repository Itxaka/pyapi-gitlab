.. python-gitlab documentation master file, created by
   sphinx-quickstart on Sun Aug 04 20:46:27 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to python-gitlab's documentation!
=========================================


python-gitlab is a wrapper to access all the functions of Gitlab from our python scripts.



How to use it
==================

There are several optional parameters in a lot of the commands, you should check the command documentation or the
command string, for example adding an user accepts up to 7 extra parameters.

First we import our library::

   import gitlab

Then we need to authenticate to our Gitlab instance. There is 2 ways of doing this.

Authenticating via user/password
==================================

First create the instance passing the gitlab server as parameter::

   git = gitlab.Gitlab("our_gitlab_host")

Then call the login() method::

   git.login("user", "password")


That's it, now your gitlab instance is using the private token in all the calls. You can see it in the token variable

Authenticating via private_token
====================================

You can also authenticate via the private_token that you can get from your gitlab profile and it's easier than using user/password

Just call the instance with the parameter token::

    git = gitlab.Gitlab("our_gitlab_host", token="mytoken")


Users
==================

There are several functions to manage users

Create user::

   git.createUser("name", "username", "password", "email")

Delete user::

   git.deleteUser(user_id)

Edit user details::

   git.editUser(user_id)

Get all the users::

   print git.getUsers()

Get the current user::

   print git.currentUser()

Get the user SSH keys::

   for key in git.getSshKeys():
       print key

Get one key for the current user, specified by the key ID::

   print git.getSshKey(key_id)

Add a new SSH key::

    git.addSshKey("key name", "actual key")

Add a new SSH key for a specified user, identified by ID::

   addSshKeyUser(user_id, "key name", "actual key")

Delete a SSH key for the current user::

   git.deleteSshKey(key_id)

Projects
===========

Get all the projects::

   project = git.getProjects()
   for proj in project:
       print proj

Get one project, identified by ID::

   git.getProject(project_id)

Get project events::

   git.getProjectEvents(project_id)

Create a new project

If you are using version 6 you can pass an extra "public" argument which makes the project public.

Please note that Gitlab 5 doesn't have this option and using it will probably end in a failure while creating the project::

   git.createProject(name, description="", default_branch="",
                      issues_enabled=0, wall_enabled=0,
                      merge_requests_enabled=0, wiki_enabled=0,
                      snippets_enabled=0, public=0)

List project members::

   git.listProjectMembers(project_id)

Add a member to a project, access_level can be master,developer,reporter or guest::

   git.addProjectMember(project_id, member_id, access_level)


Edit a project member, access_level can be master,developer,reporter or guest::

   git.editProjectMember(id_, user_id, access_level)

Delete a member from a project::

   git.deleteProjectMember(project_id, member_id)

Get the project Readme, you have to pass the web_url that getProject() provides::

    git.getReadme(proj['web_url'])

Move a project::

    git.moveProject(groupID, projectID)

Hooks
=====

Get all the hooks::

   git.getProjectHooks(project_id)

Get one hook, identified by ID::

   git.getProjectHook(project_id, hook_id)

Edit one hook::

   git.editProjectHook(id_, hook_id, url)

Add a hook to a project::

    git.addProjectHook(project_id, url_hook)

Delete a hook from a project::

    git.deleteProjectHook(project_id, hook_id)

Branches
========

Get all the branches for a project::

   git.listBranches(1)

Get a specific branch for a project::

   git.listBranch(1, "master")

Protect a branch::

   git.protectBranch(1, "master")

Unprotect a branch::

   git.unprotectBranch(1, "master")

Create a relation between two projects (The usual "forked from xxxxx")::

   git.createForkRelation(1, 3)

Remove fork relation::

   git.removeForkRelation(1)


Issues
======

Get all the issues::

   get.getIssues()

Get a project issues::

   git.getProjectIssues(1)

Get a specified issue from a project::

   git.getProjectIssue(1,1)

Create an issue::

   git.createIssue(1, "pedsdfdwsdne")

Edit an issue, you can pass state_event="closed" to close it::

   git.editIssue(1,1, title="Changing title")


Milestones
==========

Get all the milestones::

   git.getMilestones(1)

Get a specific milestone from a project::

   git.getMilestone(1,1)

Create a new milestone::

   git.createMilestone(1,"New milestone")

Edit a milestone, you can pass state_event="closed" to close it::

   git.editMilestone(1,1,title="Change milestone title")

Deploy Keys
===========
Get all the deployed keys for a project::

   git.listdeployKeys(id_)

Get one key for a project::

   git.listDeployKey(id_, key_id)

Add a key to a project::

   git.addDeployKey(id_, title, key)

Delete a key from a project::

   git.deleteDeployKey(id_, key_id)

Groups
========

Create a group::

    def createGroup(self, name, path):

Get a group. If none are specified returns all the groups::

    def getGroups(self, id_=None):

Merge support
==============

Get all the merge requests for a project::

    git.getMergeRequests(projectID, page=None, per_page=None)

Get information about a specific merge request::

    git.getMergeRequest(projectID, mergeRequestID)

Create a new merge request::

    git.reateMergeRequest(projectID, sourceBranch, targetBranch, title, assigneeID=None)

Update an existing merge request::

    git.updateMergeRequest(projectID, mergeRequestID, sourceBranch=None, targetBranch=None, title=None, assigneeID=None, closed=None)

Add a comment to a merge request::

    git.addCommentToMergeRequest(projectID, mergeRequestID, note)

