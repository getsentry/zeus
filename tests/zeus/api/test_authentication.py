import pytest

from zeus import factories
from zeus.api.authentication import ApiTokenAuthentication, AuthenticationFailed


def test_no_header(app):
    with app.test_request_context('/'):
        assert not ApiTokenAuthentication().authenticate()


def test_invalid_authentication_type(app):
    with app.test_request_context('/', headers={'Authentication': 'foobar'}):
        assert not ApiTokenAuthentication().authenticate()


def test_invalid_token(app):
    with app.test_request_context('/', headers={'Authentication': 'Bearer: foobar'}):
        with pytest.raises(AuthenticationFailed):
            ApiTokenAuthentication().authenticate()


def test_expired_token(app):
    api_token = factories.ApiTokenFactory(expired=True)
    with app.test_request_context(
        '/', headers={'Authentication': 'Bearer: {}'.format(api_token.access_token)}
    ):
        with pytest.raises(AuthenticationFailed):
            ApiTokenAuthentication().authenticate()


def test_valid_token(app, default_api_token):
    with app.test_request_context(
        '/', headers={'Authentication': 'Bearer: {}'.format(default_api_token.access_token)}
    ):
        tenant = ApiTokenAuthentication().authenticate()
        assert tenant.token_id == default_api_token.id
