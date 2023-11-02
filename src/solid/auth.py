import httpx
from httpx import Response

from solid_oidc_client import SolidOidcClient, SolidAuthSession, MemStore
import flask

from multiprocessing import Process, Queue

from typing import Dict


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

        if not r.is_redirect:
            r.raise_for_status()

        if not self.is_login:
            raise Exception('Cannot login.')


class OidcAuth:

    OAUTH_CALLBACK_PATH = '/oauth/callback'
    OAUTH_CALLBACK_URI = f"http://localhost:8080{OAUTH_CALLBACK_PATH}"

    def __init__(self):
        self.client = httpx.Client()
        self.session = None
        self._server_process = None

    @property
    def is_login(self) -> bool:
        return self.session is not None

    def fetch(self, method, url, options: Dict) -> Response:
        if 'headers' not in options:
            options['headers'] = {}

        if self.session:
            auth_headers = self.session.get_auth_headers(url, method)
            options['headers'].update(auth_headers)

        r = self.client.request(method, url, **options)
        return r

    def _start_server(self, solid_oidc_client: SolidOidcClient, q: Queue):
        process = Process(target=_run_flask_server, args=(solid_oidc_client, q))
        self._server_process = process
        process.start()

    def _stop_server(self):
        self._server_process.terminate()

    def login(self, idp):
        solid_oidc_client = SolidOidcClient(storage=MemStore())
        solid_oidc_client.register_client(idp, [OidcAuth.OAUTH_CALLBACK_URI])
        login_url = solid_oidc_client.create_login_uri('/', OidcAuth.OAUTH_CALLBACK_URI)
        q = Queue(1)
        self._start_server(solid_oidc_client, q)

        print(f"Please visit this URL to log-in: {login_url}")

        session = SolidAuthSession.deserialize(q.get())
        self.session = session

        self._stop_server()


def _run_flask_server(solid_oidc_client: SolidOidcClient, q: Queue):
    app = flask.Flask(__name__)

    @app.get('/oauth/callback')
    def login_callback():
        code = flask.request.args['code']
        state = flask.request.args['state']

        session = solid_oidc_client.finish_login(
            code=code,
            state=state,
            callback_uri=OidcAuth.OAUTH_CALLBACK_URI,
        )

        q.put(session.serialize())

        return flask.Response(
                            f"Logged in as {session.get_web_id()}. You can close your browser now.",
                            mimetype='text/html')

    app.run('localhost', 8080)
