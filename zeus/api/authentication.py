from flask import request

from zeus import auth
from zeus.utils.sentry import span


class HeaderAuthentication(object):
    @span("auth.header")
    def authenticate(self):
        return auth.get_tenant_from_headers(request.headers)


class SessionAuthentication(object):
    @span("auth.session")
    def authenticate(self):
        user = auth.get_current_user()
        if not user:
            return None

        return auth.Tenant.from_user(user)
