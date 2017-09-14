# -*- coding: utf-8 -*-
import requests

from .base import Base
from .helper import deprecated


class Users(Base):
    def get_users(self, search=None, page=1, per_page=20, **kwargs):
        """
        Returns a list of users from the Gitlab server

        :param search: Optional search query
        :param page: Page number (default: 1)
        :param per_page: Number of items to list per page (default: 20, max: 100)
        :return: List of Dictionaries containing users
        :raise: HttpError if invalid response returned
        """
        if search:
            return self.get('/users', page=page, per_page=per_page, search=search, **kwargs)

        return self.get('/users', page=page, per_page=per_page, **kwargs)

    @deprecated
    def getusers(self, search=None, page=1, per_page=20, **kwargs):
        """
        Returns a list of users from the Gitlab server

        .. warning:: Warning this is being deprecated please use :func:`gitlab.Gitlab.get_users`

        :param search: Optional search query
        :param page: Page number (default: 1)
        :param per_page: Number of items to list per page (default: 20, max: 100)
        :return: returns a dictionary of the users, false if there is an error
        """
        return self.get_users(search=search, page=page, per_page=per_page, **kwargs)

    def getuser(self, user_id):
        """
        Get info for a user identified by id

        :param user_id: id of the user
        :return: False if not found, a dictionary if found
        """
        request = requests.get(
            '{0}/{1}'.format(self.users_url, user_id),
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
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
        data = {'name': name, 'username': username, 'password': password, 'email': email}

        if kwargs:
            data.update(kwargs)

        request = requests.post(
            self.users_url, headers=self.headers, data=data,
            verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 201:
            return request.json()
        elif request.status_code == 404:
            return False

    def delete_user(self, user):
        """
        Deletes a user. Available only for administrators.
        This is an idempotent function, calling this function for a non-existent user id
        still returns a status code 200 OK.
        The JSON response differs if the user was actually deleted or not.
        In the former the user is returned and in the latter not.

        :param user: The ID of the user
        :return: Empty Dict
        :raise: HttpError: If invalid response returned
        """
        return self.delete('/users/{user}'.format(user=user), default_response={})

    @deprecated
    def deleteuser(self, user_id):
        """
        Deletes a user. Available only for administrators.
        This is an idempotent function, calling this function for a non-existent user id
        still returns a status code 200 OK.
        The JSON response differs if the user was actually deleted or not.
        In the former the user is returned and in the latter not.

        .. warning:: Warning this is being deprecated please use :func:`gitlab.Gitlab.delete_user`

        :param user_id: The ID of the user
        :return: True if it deleted, False if it couldn't
        """
        deleted = self.delete_user(user_id)

        if deleted is False:
            return False
        else:
            return True

    def currentuser(self):
        """
        Returns the current user parameters. The current user is linked to the secret token

        :return: a list with the current user properties
        """
        request = requests.get(
            '{0}/api/v3/user'.format(self.host),
            headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        return request.json()

    def edituser(self, user_id, **kwargs):
        """
        Edits an user data.

        :param user_id: id of the user to change
        :param kwargs: Any param the the Gitlab API supports
        :return: Dict of the user
        """
        data = {}

        if kwargs:
            data.update(kwargs)

        request = requests.put(
            '{0}/{1}'.format(self.users_url, user_id),
            headers=self.headers, data=data, timeout=self.timeout, verify=self.verify_ssl, auth=self.auth)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def blockuser(self, user_id, **kwargs):
        """
        Block a user.

        :param user_id: id of the user to change
        :param kwargs: Any param the the Gitlab API supports
        :return: Dict of the user
        """
        data = {}

        if kwargs:
            data.update(kwargs)

        request = requests.put(
            '{0}/{1}/block'.format(self.users_url, user_id),
            headers=self.headers, data=data, timeout=self.timeout, verify=self.verify_ssl)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def getsshkeys(self):
        """
        Gets all the ssh keys for the current user

        :return: a dictionary with the lists
        """
        request = requests.get(
            self.keys_url, headers=self.headers, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 200:
            return request.json()
        else:
            return False

    def addsshkey(self, title, key):
        """
        Add a new ssh key for the current user

        :param title: title of the new key
        :param key: the key itself
        :return: true if added, false if it didn't add it (it could be because the name or key already exists)
        """
        data = {'title': title, 'key': key}

        request = requests.post(
            self.keys_url, headers=self.headers, data=data,
            verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 201:
            return True
        else:
            return False

    def addsshkeyuser(self, user_id, title, key):
        """
        Add a new ssh key for the user identified by id

        :param user_id: id of the user to add the key to
        :param title: title of the new key
        :param key: the key itself
        :return: true if added, false if it didn't add it (it could be because the name or key already exists)
        """
        data = {'title': title, 'key': key}

        request = requests.post(
            '{0}/{1}/keys'.format(self.users_url, user_id), headers=self.headers,
            data=data, verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.status_code == 201:
            return True
        else:
            return False

    def deletesshkey(self, key_id):
        """
        Deletes an sshkey for the current user identified by id

        :param key_id: the id of the key
        :return: False if it didn't delete it, True if it was deleted
        """
        request = requests.delete(
            '{0}/{1}'.format(self.keys_url, key_id), headers=self.headers,
            verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        if request.content == b'null':
            return False
        else:
            return True
