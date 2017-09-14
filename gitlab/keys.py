from gitlab.base import Base
from gitlab.helper import deprecated


class Keys(Base):
    def keys(self, key_id):
        """
        Get SSH key with user by ID of an SSH key. Note only administrators can lookup SSH key with user by ID of an
        SSH key.

        >>> gitlab = Gitlab(host='http://localhost:10080', verify_ssl=False)
        >>> gitlab.login(user='root', password='5iveL!fe')
        >>> gitlab.keys(1)

        :param key_id: The ID of an SSH key
        :return: Dictionary containing Key data
        """
        return self.get('/keys/{key_id}'.format(key_id=key_id), default_response={})

    @deprecated
    def getsshkey(self, key_id):
        """
        Get a single ssh key identified by key_id

        .. warning:: Warning this is being deprecated please use :func:`gitlab.Gitlab.keys`

        >>> gitlab = Gitlab(host='http://localhost:10080', verify_ssl=False)
        >>> gitlab.login(user='root', password='5iveL!fe')
        >>> gitlab.getsshkeys(1)

        :param key_id: The ID of an SSH key
        :return: Dictionary containing Key data
        """
        return self.keys(key_id)
