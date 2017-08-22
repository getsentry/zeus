import responses

from datetime import datetime
from flask import current_app
from oauth2client.client import OAuth2Credentials

from zeus.models import Identity, User
from zeus.constants import GITHUB_AUTH_URI, GITHUB_TOKEN_URI


def test_login(client):
    resp = client.get('/auth/github')
    assert resp.status_code == 302
    assert resp.headers['Location'] == \
        '{}?client_id=github.client-id&redirect_uri=http%3A%2F%2Flocalhost%2Fauth%2Fgithub%2Fcomplete&scope=user%3Aemail%2Cread%3Aorg&access_type=offline&response_type=code'.format(
            GITHUB_AUTH_URI)


def test_login_complete(client, mocker):
    mock_step2_exchange = mocker.patch(
        'zeus.web.views.auth_github.OAuth2WebServerFlow.step2_exchange'
    )

    responses.add(
        'GET',
        'https://api.github.com/user?access_token=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
        match_querystring=True,
        body='{"id": 1, "login": "test", "email": "foo@example.com"}'
    )

    access_token = 'b' * 40
    refresh_token = 'c' * 40

    mock_step2_exchange.return_value = OAuth2Credentials(
        access_token,
        current_app.config['GITHUB_CLIENT_ID'],
        current_app.config['GITHUB_CLIENT_SECRET'],
        refresh_token,
        datetime(2013, 9, 19, 22, 15, 22),
        GITHUB_TOKEN_URI,
        'foo/1.0',
        token_response={
            'scope': 'user:email,read:org',
        },
    )

    resp = client.get('/auth/github/complete?code=abc')

    mock_step2_exchange.assert_called_once_with('abc')

    assert resp.status_code == 302
    assert resp.headers['Location'] == 'http://localhost/'

    user = User.query.filter(
        User.email == 'foo@example.com',
    ).first()

    assert user

    identity = Identity.query.filter(
        Identity.user_id == user.id,
    ).first()

    assert identity
    assert identity.provider == 'github'
    assert identity.external_id == '1'
    assert identity.config == {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'login': 'test',
        'scopes': ['user:email', 'read:org'],
    }
