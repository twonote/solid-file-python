import httpx


class Auth:
    def __init__(self):
        self.client = httpx.Client()

    @property
    def is_login(self) -> bool:
        return self.client.cookies.get('nssidp.sid') is not None

    def login(self, idp, username, password):
        # NSS only
        if idp[-1] == '/':
            idp = idp[:-1]
        url = '/'.join((idp, 'login/password'))

        data = {
            'username': username,
            'password': password
        }

        r = self.client.post(url, data=data)
        r.raise_for_status()

        if not self.is_login:
            raise Exception('Cannot login.')
