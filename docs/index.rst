.. pyapi-gitlab documentation master file, created by
   sphinx-quickstart on Sun Aug 04 20:46:27 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pyapi-gitlab's documentation!
=========================================

pyapi-gitlab is a wrapper to access all the functions of Gitlab from our python scripts.


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


Using sudo on the functions
=============================

From version 6, gitlab accepts a sudo parameter in order to execute an order as if you were another user.
This has been implemente in pyapi-gitlab on the following functions:

   getusers()
   
   createuser()
   
   edituser()
   
   addsshkey()
   
   addsshkeyuser()
   
   getprojects()
   
   createproject()
   
   createprojectuser()
   
   addprojectmember()
   
   editprojectmember()
   
   editprojecthook()
   
   getissues()
   
   getprojectissues()
   
   createissue()
   
   editissue()
   
   createmilestone()
   
   editmilestone()
   
   adddeploykey()
   
   getgroups()
   
   getmergerequests()
   
   createmergerequest()
   
   updatemergerequest()
   


All you need to do is add a sudo="user" parameter when calling the function like this::

   git.createuser("name", "username", "password", "email", sudo="admin")


Pagination
===========

The following functions now accept pagination:

    getusers()

    getprojects()

    getprojectevents()

    getissues()

    getprojectissues()

    getgroups()

    getmergerequests()

    listprojectmembers()


You can pass 2 parameters: page= and per_page= to them in order to get a especific page or change the results per page::

    git.getissues(page=1, per_page=40)


The default is to get page 1 and 20 results per page. The max value for per_page is 100.

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

   print git.getusers(search=None)

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

Delete a project::

    git.deleteproject(project_id)

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

Create a branch::

   git.createbranch(1, "newbranch", "7b5c3cc8be40ee161ae89a06bba6229da1032a0c")

Delete a branch::

   git.deletebranch(1, "newbranch")

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

Edit an issue, you can pass state_event="close" to close it::

   git.editissue(1,1, title="Changing title")


Milestones
==========

Get all the milestones::

   git.getmilestones(1)

Get a specific milestone from a project::

   git.getmilestone(1,1)

Create a new milestone::

   git.createmilestone(1,"New milestone")

Edit a milestone, you can pass state_event="close" to close it::

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

    git.creategroup(self, name, path):

Delete a group::

    git.deletegroup(group_id)

Get a group. If none are specified returns all the groups::

    git.getgroups(self, id_=None):

List group members::

    git.listgroupmembers(group_id)

Add a member to a group::

    git.addgroupmember(group_id, user_id, access_level, sudo="")

Delete a member from a group::

    git.deletegroupmember(group_id, user_id)


Merge support
==============

Get all the merge requests for a project::

    git.getmergerequests(projectID, page=None, per_page=None)

Get information about a specific merge request::

    git.getmergerequest(projectID, mergeRequestID)

Get comments of a merge request::

    git.getmergerequestcomments(projectID, mergeRequestID, page=1, per_page=20):

Create a new merge request::

    git.createmergerequest(projectID, sourceBranch, targetBranch, title, assigneeID=None)

Update an existing merge request::

    git.updatemergerequest(projectID, mergeRequestID, sourceBranch=None, targetBranch=None, title=None, assigneeID=None, closed=None)

Accept existing merge request::

    acceptmergerequest(projectID, mergeRequestID, title=None)

Add a comment to a merge request::

    git.addcommenttomergerequest(projectID, mergeRequestID, note)

Snippets
==========

Get all the snippets from a project::

    git.getsnippets(project_id)

Get one snippet from a project::

    git.getsnippet(project_id, snippet_id)

Create a new snippet::

    git.createsnippet(project_id, title, file_name, code, lifetime="")

Get a snippet content(raw content)::

    git.getsnippetcontent(project_id, snippet_id)

Delete a snippet::

    git.deletesnippet(project_id, snippet_id)

Repositories
==============

Caution: Gitlab has a mixed feeling of repositories/projects. For example, to get the commits for a project you call the listrepositorycommits part, same with the tags.
Have that in mind when working with commits and such, as I believe it should be included into the projects part and it may chage to that in the future.


Get all the repositories for a project::

    git.getrepositories(project_id)

Get a branch from a repository::

    git.getrepositorybranch(project_id, branch_name)

Protect a repository branch::

    git.protectrepositorybranch(project_id, branch_name)

Unprotect a repository branch::

    git.unprotectrepositorybranch(project_id, branch_name)

List the the project tags::

    git.listrepositorytags(project_id)

List the the project commits::

    git.listrepositorycommits(project_id)

List on commit from a project::

    git.listrepositorycommit(project_id, sha1)


List the complete diff, lines changed included::

    git.listrepositorycommitdiff(project_id, sha1)

List the project tree, files and dirs. Use the path to explore subdirs::

    git.listrepositorytree(project_id, path="", ref_name="")

Get the raw blob from a project file::

    git.getrawblob(project_id, sha1, path)

Compare branches, tags or commits::

    git.compare_branches_tags_commits(project_id, from_id, to_id)

Notes (from projects, issues, snippets)
=======================================
Get a project wall notes::

    git.getprojectwallnotes(project_id)

Get one specific wall note from a project::

    git.getprojectwallnote(project_id, note_id)

Create a wall note for a project::

    git.createprojectwallnote(project_id, content)

Get all the notes from an issue wall::

    git.getissuewallnotes(project_id, issued_id)

Get one note from an issue wall::

    git.getissuewallnote(project_id, issue_id, note_id)

Create a note in the wall of an issue::

    git.createissuewallnote(project_id, issue_id, content)


Get all the notes from a snippet wall::

    git.getsnippetwallnotes(project_id, snippet_id)

Get one note from a snippet wall::

    git.getsnippetwallnote(project_id, snippet_id, note_id)

Create a note in the wall of a snippet::

    git.createsnippetewallnote(project_id, snippet_id, content)

Get all the notes from a merge request wall::

    git.getmergerequestwallnotes(project_id, merge_request_id)

Get one note from a merge request wall::

    git.getmergerequestwallnote(project_id, merge_request_id, note_id)

Creat a note in the wall of a merge request::

    git.createmergerequestewallnote(project_id, merge_request_id, content)
    
Files
=====

Create a new file in the repository::

    git.createfile(project_id, file_path, branch_name, content, commit_message)

Get a file::

    git.getfile(self, project_id, file_path, ref):

Update an existing file::

    git.updatefile(project_id, file_path, branch_name, content, commit_message)
    
Deleting a file::

    git.deletefile(project_id, file_path, branch_name, commit_message)

Examples
=========

Getting the SHA1 of the commit
===============================
To call this, you need to pass the actual hash of the commit. You can access the sha1 by doing this::

    git.listrepositorycommits(project_id)

This would return a list of dicts with all the commits for that project. You can extract the sha1 of the commit by
accessing the commit you want and using the key 'id' like this::

    git.listrepositorycommits(2)[0]['id']

In turn the whole thing (that is, if you know which commit number you need) would turn like this::

    git.listrepositorycommit(2, self.git.listrepositorycommits(2)[0]['id'])

