import os

from gitlab import Gitlab

host = os.environ.get('gitlab_host', 'http://gitlab:80')
user = os.environ.get('gitlab_user', 'root')
password = os.environ.get('gitlab_password', '5iveL!fe')

gitlab = Gitlab(host=host, verify_ssl=False)

gitlab_responding = False
while not gitlab_responding:
    try:
        response = gitlab.login(user=user, password=password)
        gitlab_responding = True
    except:
        pass

exit(0)
