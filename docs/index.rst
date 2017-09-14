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

Then we need to authenticate to our Gitlab instance. There is 3 ways of doing this.

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


Authenticating via oAuth2 token
====================================

You can also authenticate via the oAuth token that you can get from your gitlab profile and it's easier than using user/password

Just call the instance with the parameter oauth_token::

    git = gitlab.Gitlab("our_gitlab_host", oauth_token="mytoken")


Using sudo on the functions
=============================

All API calls support using sudo (e.g. calling the API as a different user)
This is accomplished by using the setsudo() method to temporarily make all requests as another user, then calling it with no args to go back to the original user::


    >>> git = gitlab.Gitlab(host=host)
    >>> git.login(user=user, password=password)
    True
    >>> git.currentuser()["username"]
    u'root'
    >>> [[u["id"], u["username"]] for u in git.getusers()]
    [[1, u'root'], [9, u'sudo_user'], [10, u'NMFUQ85Y']]
    >>> # lets try with sudo_user
    >>> git.setsudo(9)
    >>> git.currentuser()["username"]
    u'sudo_user'
    >>> # lets change back to the original user
    >>> git.setsudo(1)
    >>> git.currentuser()["username"]
    u'root'



Pagination
===========

All get* functions now accept a page and per_page parameter::

    git.getissues(page=1, per_page=40)


The default is to get page 1 and 20 results per page. The max value for per_page is 100.


Getting all results
====================

There is a getall method which will return all results for any call that accepts pagination::

    git.getall(git.getprojects)

Used in loops::

    for project in git.getall(git.getprojects):
        pass

Treated as a generator::

    print ", ".join(user['username'] for user in git.getall(git.getusers, per_page=100))

Wrap with list() which retrieves all the elements::

    print 'number of users: %d' % len(list(git.getall(git.getusers)))

Start from any page::

    # skip the first 4400 results
    len(list(git.getall(git.getusers, page=51, per_page=80)))

And with positional args::

    print len(list(git.getall(git.getgroupmembers, 191, page=3, per_page=7)))


API Deprecation
==================

We are currently working on moving to new method names but don't want to break any existing code bases. In order for
us to do this we will be adding a deprecation warning to the old style methods. Please find below an example of how
things will change.

Code Example::

    # The old style to get users
    getusers('bob')

    # the new style
    get_users('bob')


API doc
==================

We are working to get back to a 1:1 translation of the Gitlab API.

Gitlab
------------------

.. autoclass:: gitlab.Gitlab
    :members:
    :inherited-members:

Base
------------------

.. autoclass:: gitlab.base.Base
    :members:

Session
------------------

.. autoclass:: gitlab.session.Session
    :members:

Keys
------------------

.. autoclass:: gitlab.keys.Keys
    :members:


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`