from .base import Base


class Session(Base):
    def login(self, email=None, password=None, user=None):
        """
        Logs the user in and setups the header with the private token

        :param email: Gitlab user Email
        :param user: Gitlab username
        :param password: Gitlab user password
        :return: True if login successful
        :raise: HttpError
        :raise: ValueError
        """
        if user is not None:
            data = {'login': user, 'password': password}
        elif email is not None:
            data = {'email': email, 'password': password}
        else:
            raise ValueError('Neither username nor email provided to login')

        self.headers = {'connection': 'close'}
        response = self.post('/session', **data)

        self.token = response['private_token']
        self.headers = {'PRIVATE-TOKEN': self.token,
                        'connection': 'close'}
        return response
