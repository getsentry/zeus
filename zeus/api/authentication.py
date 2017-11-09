from flask import g, request
from sqlalchemy.orm import joinedload

from zeus import auth
from zeus.models import ApiToken, RepositoryApiToken, UserApiToken


class AuthenticationFailed(Exception):
    pass


class ApiTokenAuthentication(object):
    def authenticate(self):
        header = request.headers.get('Authorization', '').lower()
        if not header:
            return None

        if not header.startswith('bearer:'):
            return None

        token = header.split(':', 1)[-1].strip()
        if not token.startswith('zeus-'):
            # Assuming this is a legacy token
            return self.authenticate_legacy(token)

        parts = token.split('-', 2)
        if not len(parts) == 3:
            raise AuthenticationFailed

        if parts[1] == 'u':
            return self.authenticate_user(parts[2])
        if parts[1] == 'r':
            return self.authenticate_repository(parts[2])

        raise AuthenticationFailed

    def authenticate_user(self, key):
        token = UserApiToken.query \
            .options(joinedload('user')) \
            .filter(UserApiToken.key == key) \
            .first()

        if not token:
            raise AuthenticationFailed

        return auth.Tenant.from_user(token.user)

    def authenticate_repository(self, key):
        token = RepositoryApiToken.query \
            .options(joinedload('repository')) \
            .filter(RepositoryApiToken.key == key) \
            .first()

        if not token:
            raise AuthenticationFailed

        return auth.Tenant.from_repository(token.repository)

    def authenticate_legacy(self, token):
        api_token = ApiToken.query.filter(
            ApiToken.access_token == token,
        ).first()

        if not api_token:
            raise AuthenticationFailed

        if api_token.is_expired():
            raise AuthenticationFailed

        if api_token:
            g.current_api_token = api_token

        return auth.Tenant.from_api_token(api_token)


class SessionAuthentication(object):
    def authenticate(self):
        user = auth.get_current_user()
        if not user:
            return None
        return auth.Tenant.from_user(user)
