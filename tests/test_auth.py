import os

from solid.auth import Auth

IDP = os.getenv('IDP')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')


def test_login():
    auth = Auth()
    assert not auth.is_login
    auth.login(IDP, USERNAME, PASSWORD)
    assert auth.is_login
