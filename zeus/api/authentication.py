from flask import g, request

from zeus import auth
from zeus.models import ApiToken


class AuthenticationFailed(Exception):
    pass


class ApiTokenAuthentication(object):
    def authenticate(self):
        header = request.headers.get('Authentication', '').lower()
        if not header:
            return None

        if not header.startswith('bearer:'):
            return None

        token = header.split(':', 1)[-1].strip()

        api_token = ApiToken.query.filter(
            ApiToken.access_token == token,
        ).first()

        if not api_token:
            raise AuthenticationFailed

        if api_token.is_expired():
            raise AuthenticationFailed

        if api_token:
            g.current_api_token = api_token

        auth.set_current_tenant(auth.Tenant.from_api_token(api_token))
        return True


class SessionAuthentication(object):
    def authenticate(self):
        user = auth.get_current_user()
        if not user:
            return None
        auth.set_current_tenant(auth.Tenant.from_user(user))
        return True
