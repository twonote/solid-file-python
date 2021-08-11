import os

from solid.auth import Auth

IDP = os.getenv('SOLID_IDP')
USERNAME = os.getenv('SOLID_USERNAME')
PASSWORD = os.getenv('SOLID_PASSWORD')


def test_login():
    auth = Auth()
    assert not auth.is_login
    auth.login(IDP, USERNAME, PASSWORD)
    assert auth.is_login
