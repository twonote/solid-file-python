try:
    from solid_oidc_client import SolidOidcClient, SolidAuthSession, MemStore
    import flask
except ImportError as e:
    raise ImportError(
        "OIDC authentication requires optional dependencies. "
        "Install them with: pip install solid-file[oidc]"
    ) from e

import httpx
from httpx import Response
from multiprocessing import Process, Queue
from urllib.parse import urlparse, parse_qs
from typing import Dict, Optional, Tuple, Callable


class OidcAuth:
    """Solid-OIDC authentication using solid-oidc-client.

    Args:
        callback_server: If True (default), starts a local Flask server to
            automatically receive the OIDC callback. If False, the user must
            manually paste the full redirect URL after logging in.
        callback_port: Port for the local callback server (default 8080).
    """

    OAUTH_CALLBACK_PATH = '/oauth/callback'

    def __init__(self, callback_server: bool = True, callback_port: int = 8080):
        self.callback_server = callback_server
        self.callback_port = callback_port
        self.callback_uri = f"http://localhost:{callback_port}{self.OAUTH_CALLBACK_PATH}"
        self.client = httpx.Client()
        self.session: Optional[SolidAuthSession] = None
        self._server_process: Optional[Process] = None

    @property
    def is_login(self) -> bool:
        return self.session is not None

    def fetch(self, method: str, url: str, options: Dict) -> Response:
        if 'headers' not in options:
            options['headers'] = {}

        if self.session:
            auth_headers = self.session.get_auth_headers(url, method)
            options['headers'].update(auth_headers)

        return self.client.request(method, url, **options)

    def login(self, idp: str) -> None:
        """Log in to the Solid identity provider.

        If callback_server=True, starts a local server to receive the OIDC
        callback automatically. If callback_server=False, prints the login URL
        and prompts you to paste the full redirect URL manually.
        """
        solid_oidc_client = SolidOidcClient(storage=MemStore())
        solid_oidc_client.register_client(idp, [self.callback_uri])
        login_url = solid_oidc_client.create_login_uri('/', self.callback_uri)

        if self.callback_server:
            self._login_with_server(solid_oidc_client, login_url)
        else:
            self._login_manual(solid_oidc_client, login_url)

    def _login_with_server(self, solid_oidc_client: SolidOidcClient, login_url: str) -> None:
        q: Queue = Queue(1)
        process = Process(target=_run_flask_server, args=(solid_oidc_client, self.callback_uri, q))
        self._server_process = process
        process.start()

        print(f"Please visit this URL to log in: {login_url}")

        session = SolidAuthSession.deserialize(q.get())
        self.session = session
        self._server_process.terminate()
        self._server_process = None

    def _login_manual(self, solid_oidc_client: SolidOidcClient, login_url: str) -> None:
        print(f"Please visit this URL to log in:\n  {login_url}")
        print(
            f"\nAfter logging in, you will be redirected to a URL starting with:\n"
            f"  {self.callback_uri}\n"
            "Please paste the full redirect URL here:"
        )
        redirect_url = input().strip()

        parsed = urlparse(redirect_url)
        params = parse_qs(parsed.query)

        code = params.get('code', [None])[0]
        state = params.get('state', [None])[0]

        if not code or not state:
            raise ValueError(
                f"Could not extract 'code' and 'state' from redirect URL: {redirect_url}"
            )

        session = solid_oidc_client.finish_login(
            code=code,
            state=state,
            callback_uri=self.callback_uri,
        )
        self.session = session


def _run_flask_server(solid_oidc_client: SolidOidcClient, callback_uri: str, q: Queue) -> None:
    app = flask.Flask(__name__)

    callback_path = '/' + callback_uri.split('/', 3)[-1]

    @app.get(callback_path)
    def login_callback():
        code = flask.request.args['code']
        state = flask.request.args['state']

        session = solid_oidc_client.finish_login(
            code=code,
            state=state,
            callback_uri=callback_uri,
        )
        q.put(session.serialize())

        return flask.Response(
            f"Logged in as {session.get_web_id()}. You can close your browser now.",
            mimetype='text/html',
        )

    port = int(callback_uri.split(':')[2].split('/')[0])
    app.run('localhost', port)
