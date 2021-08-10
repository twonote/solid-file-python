import httpx


class Auth:
    def __init__(self):
        self.client = httpx.Client()

    @property
    def is_login(self) -> bool:
        return self.client.cookies.get('nssidp.sid') is not None

    def login(self, idp, username, password):
        # NSS only
        url = '/'.join((idp, 'login/password'))

        data = {
            'username': username,
            'password': password
        }

        self.client.post(url, data=data)

        if not self.is_login:
            raise Exception('Cannot login.')
