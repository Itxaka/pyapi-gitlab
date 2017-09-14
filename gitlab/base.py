# -*- coding: utf-8 -*-
import requests


class Base(object):
    """
    Base class

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
    def __init__(self, host, token=None, oauth_token=None, verify_ssl=True, auth=None, timeout=None,
                 suppress_http_error=True):
        self.suppress_http_error = suppress_http_error

        if token:
            self.token = token
            self.headers = {'PRIVATE-TOKEN': self.token}

        if oauth_token:
            self.oauth_token = oauth_token
            self.headers = {'Authorization': 'Bearer {}'.format(
                self.oauth_token)}

        if not host:
            raise ValueError('host argument may not be empty')

        self.host = host.rstrip('/')

        if self.host.startswith('http://') or self.host.startswith('https://'):
            pass
        else:
            self.host = 'https://' + self.host

        self.auth = auth
        self.api_url = self.host + '/api/v3'
        self.projects_url = self.api_url + '/projects'
        self.users_url = self.api_url + '/users'
        self.keys_url = self.api_url + '/user/keys'
        self.groups_url = self.api_url + '/groups'
        self.search_url = self.api_url + '/projects/search'
        self.hook_url = self.api_url + '/hooks'
        self.namespaces_url = self.api_url + '/namespaces'
        self.verify_ssl = verify_ssl
        self.timeout = timeout

    def get(self, uri, default_response=None, **kwargs):
        """
        Call GET on the Gitlab server

        >>> gitlab = Gitlab(host='http://localhost:10080', verify_ssl=False)
        >>> gitlab.login(user='root', password='5iveL!fe')
        >>> gitlab.get('/users/5')

        :param uri: String with the URI for the endpoint to GET from
        :param default_response: Return value if JSONDecodeError
        :param kwargs: Key word arguments to use as GET arguments
        :return: Dictionary containing response data
        :raise: HttpError: If invalid response returned
        """
        url = self.api_url + uri
        response = requests.get(url, params=kwargs, headers=self.headers,
                                verify=self.verify_ssl, auth=self.auth,
                                timeout=self.timeout)

        return self.success_or_raise(response, default_response=default_response)

    def post(self, uri, default_response=None, **kwargs):
        """
        Call POST on the Gitlab server

        >>> gitlab = Gitlab(host='http://localhost:10080', verify_ssl=False)
        >>> gitlab.login(user='root', password='5iveL!fe')
        >>> password = 'MyTestPassword1'
        >>> email = 'example@example.com'
        >>> data = {'name': 'test', 'username': 'test1', 'password': password, 'email': email}
        >>> gitlab.post('/users/5', **data)

        :param uri: String with the URI for the endpoint to POST to
        :param default_response: Return value if JSONDecodeError
        :param kwargs: Key word arguments representing the data to use in the POST
        :return: Dictionary containing response data
        :raise: HttpError: If invalid response returned
        """
        url = self.api_url + uri

        response = requests.post(
            url, headers=self.headers, data=kwargs,
            verify=self.verify_ssl, auth=self.auth, timeout=self.timeout)

        return self.success_or_raise(response, default_response=default_response)

    def delete(self, uri, default_response=None):
        """
        Call DELETE on the Gitlab server

        >>> gitlab = Gitlab(host='http://localhost:10080', verify_ssl=False)
        >>> gitlab.login(user='root', password='5iveL!fe')
        >>> gitlab.delete('/users/5')

        :param uri: String with the URI you wish to delete
        :param default_response: Return value if JSONDecodeError
        :return: Dictionary containing response data
        :raise: HttpError: If invalid response returned
        """
        url = self.api_url + uri
        response = requests.delete(
            url, headers=self.headers, verify=self.verify_ssl,
            auth=self.auth, timeout=self.timeout)

        return self.success_or_raise(response, default_response=default_response)

    def success_or_raise(self, response, default_response=None):
        """
        Check if request was successful or raises an HttpError

        :param response: Response Object to check
        :param default_response: Return value if JSONDecodeError
        :returns dict: Dictionary containing response data
        :returns bool: :obj:`False` on failure when exceptions are suppressed
        :raises requests.exceptions.HTTPError: If invalid response returned
        """
        if self.suppress_http_error and not response.ok:
            return False

        response_json = default_response
        if response_json is None:
            response_json = {}

        response.raise_for_status()

        try:
            response_json = response.json()
        except ValueError:
            pass

        return response_json

    @staticmethod
    def getall(fn, page=None, *args, **kwargs):
        """
        Auto-iterate over the paginated results of various methods of the API.
        Pass the GitLabAPI method as the first argument, followed by the
        other parameters as normal. Include `page` to determine first page to poll.
        Remaining kwargs are passed on to the called method, including `per_page`.

        :param fn: Actual method to call
        :param page: Optional, page number to start at, defaults to 1
        :param args: Positional arguments to actual method
        :param kwargs: Keyword arguments to actual method
        :return: Yields each item in the result until exhausted, and then implicit StopIteration; or no elements if error
        """
        if not page:
            page = 1

        while True:
            results = fn(*args, page=page, **kwargs)

            if not results:
                break
            for x in results:
                yield x

            page += 1
