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

   git.createuser("name", "username", "password", "email")

Delete user::

   git.deleteuser(user_id)

Edit user details::

   git.edituser(user_id)

Get all the users::

   print git.getusers()

Get the current user::

   print git.currentuser()

Get the user SSH keys::

   for key in git.getsshkeys():
       print key

Get one key for the current user, specified by the key ID::

   print git.getsshkey(key_id)

Add a new SSH key::

    git.addsshkey("key name", "actual key")

Add a new SSH key for a specified user, identified by ID::

   addsshkeyuser(user_id, "key name", "actual key")

Delete a SSH key for the current user::

   git.deletesshkey(key_id)

Projects
===========

Get all the projects::

   project = git.getprojects()
   for proj in project:
       print proj

Get one project, identified by ID::

   git.getproject(project_id)

Get project events::

   git.getprojectevents(project_id)

Create a new project

If you are using version 6 you can pass an extra "public" argument which makes the project public.

Please note that Gitlab 5 doesn't have this option and using it will probably end in a failure while creating the project::

   git.createproject(name, description="", default_branch="",
                      issues_enabled=0, wall_enabled=0,
                      merge_requests_enabled=0, wiki_enabled=0,
                      snippets_enabled=0, public=0)

List project members::

   git.listprojectmembers(project_id)

Add a member to a project, access_level can be master,developer,reporter or guest::

   git.addprojectmember(project_id, member_id, access_level)


Edit a project member, access_level can be master,developer,reporter or guest::

   git.editprojectmember(id_, user_id, access_level)

Delete a member from a project::

   git.deleteprojectmember(project_id, member_id)

Get the project Readme, you have to pass the web_url that getproject() provides::

    git.getreadme(proj['web_url'])

Move a project::

    git.moveproject(groupID, projectID)

Hooks
=====

Get all the hooks::

   git.getprojecthooks(project_id)

Get one hook, identified by ID::

   git.getprojecthook(project_id, hook_id)

Edit one hook::

   git.editprojecthook(id_, hook_id, url)

Add a hook to a project::

    git.addprojecthook(project_id, url_hook)

Delete a hook from a project::

    git.deleteprojecthook(project_id, hook_id)

Branches
========

Get all the branches for a project::

   git.listbranches(1)

Get a specific branch for a project::

   git.listbranch(1, "master")

Protect a branch::

   git.protectbranch(1, "master")

Unprotect a branch::

   git.unprotectbranch(1, "master")

Create a relation between two projects (The usual "forked from xxxxx")::

   git.createforkrelation(1, 3)

Remove fork relation::

   git.removeforkrelation(1)


Issues
======

Get all the issues::

   get.getissues()

Get a project issues::

   git.getprojectissues(1)

Get a specified issue from a project::

   git.getprojectissue(1,1)

Create an issue::

   git.createissue(1, "pedsdfdwsdne")

Edit an issue, you can pass state_event="closed" to close it::

   git.editissue(1,1, title="Changing title")


Milestones
==========

Get all the milestones::

   git.getmilestones(1)

Get a specific milestone from a project::

   git.getmilestone(1,1)

Create a new milestone::

   git.createmilestone(1,"New milestone")

Edit a milestone, you can pass state_event="closed" to close it::

   git.editmilestone(1,1,title="Change milestone title")

Deploy Keys
===========
Get all the deployed keys for a project::

   git.listdeploykeys(id_)

Get one key for a project::

   git.listdeploykey(id_, key_id)

Add a key to a project::

   git.adddeploykey(id_, title, key)

Delete a key from a project::

   git.deletedeploykey(id_, key_id)

Groups
========

Create a group::

    def creategroup(self, name, path):

Get a group. If none are specified returns all the groups::

    def getgroups(self, id_=None):

Merge support
==============

Get all the merge requests for a project::

    git.getmergerequests(projectID, page=None, per_page=None)

Get information about a specific merge request::

    git.getmergerequest(projectID, mergeRequestID)

Create a new merge request::

    git.reateMergeRequest(projectID, sourceBranch, targetBranch, title, assigneeID=None)

Update an existing merge request::

    git.updatemergerequest(projectID, mergeRequestID, sourceBranch=None, targetBranch=None, title=None, assigneeID=None, closed=None)

Add a comment to a merge request::

    git.addcommenttomergerequest(projectID, mergeRequestID, note)

