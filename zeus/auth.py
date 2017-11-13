import re

from cached_property import cached_property
from datetime import datetime
from flask import current_app, g, request, session
from itsdangerous import BadSignature, JSONWebSignatureSerializer
from sqlalchemy.orm import joinedload
from typing import List, Optional
from urllib.parse import urlparse, urljoin

from zeus.config import db
from zeus.exceptions import AuthenticationFailed
from zeus.models import (
    ApiToken, ApiTokenRepositoryAccess, Repository, RepositoryAccess, RepositoryApiToken, User, UserApiToken
)
from zeus.utils import timezone


class Tenant(object):
    def __init__(self, repository_ids: Optional[str]=None):
        self.repository_ids = repository_ids or []

    def __repr__(self):
        return '<{} repository_ids={}>'.format(type(self).__name__, self.repository_ids)

    @classmethod
    def from_user(cls, user: User):
        if not user:
            return cls()

        g.current_user = user
        return UserTenant(user_id=user.id)

    @classmethod
    def from_repository(cls, repository: Repository):
        if not repository:
            return cls()

        return RepositoryTenant(repository_id=repository.id)

    @classmethod
    def from_api_token(cls, token: ApiToken):
        if not token:
            return cls()

        return ApiTokenTenant(token_id=token.id)


class ApiTokenTenant(Tenant):
    def __init__(self, token_id: str):
        self.token_id = token_id

    def __repr__(self):
        return '<{} token_id={}>'.format(type(self).__name__, self.token_id)

    @cached_property
    def repository_ids(self) -> List:
        if not self.token_id:
            return None

        return [
            r[0]
            for r in db.session.query(ApiTokenRepositoryAccess.repository_id).filter(
                ApiTokenRepositoryAccess.apitoken_id == self.token_id,
            )
        ]


class UserTenant(Tenant):
    def __init__(self, user_id: str):
        self.user_id = user_id

    def __repr__(self):
        return '<{} user_id={}>'.format(type(self).__name__, self.user_id)

    @cached_property
    def repository_ids(self) -> List:
        if not self.user_id:
            return None

        return [
            r[0]
            for r in db.session.query(RepositoryAccess.repository_id).filter(
                RepositoryAccess.user_id == self.user_id,
            )
        ]


class RepositoryTenant(Tenant):
    def __init__(self, repository_id: str):
        self.repository_id = repository_id

    def __repr__(self):
        return '<{} repository_id={}>'.format(type(self).__name__, self.repository_id)

    @cached_property
    def repository_ids(self) -> List:
        if not self.repository_id:
            return None

        return [self.repository_id]


def get_tenant_from_token():
    header = request.headers.get('Authorization', '').lower()
    if not header:
        return None

    if not header.startswith('bearer'):
        return None

    token = re.sub(r"^bearer(:|\s)\s*", '', header).strip()
    if not token.startswith('zeus-'):
        # Assuming this is a legacy token
        return get_tenant_from_legacy_token(token)

    parts = token.split('-', 2)
    if not len(parts) == 3:
        raise AuthenticationFailed

    if parts[1] == 'u':
        return get_tenant_from_user_token(parts[2])
    if parts[1] == 'r':
        return get_tenant_from_repository_token(parts[2])

    raise AuthenticationFailed


def get_tenant_from_user_token(key):
    token = UserApiToken.query \
        .options(joinedload('user')) \
        .filter(UserApiToken.key == key) \
        .first()

    if not token:
        raise AuthenticationFailed

    return Tenant.from_user(token.user)


def get_tenant_from_repository_token(key):
    token = RepositoryApiToken.query \
        .options(joinedload('repository')) \
        .filter(RepositoryApiToken.key == key) \
        .first()

    if not token:
        raise AuthenticationFailed

    return Tenant.from_repository(token.repository)


def get_tenant_from_legacy_token(token):
    api_token = ApiToken.query.filter(
        ApiToken.access_token == token,
    ).first()

    if not api_token:
        raise AuthenticationFailed

    if api_token.is_expired():
        raise AuthenticationFailed

    if api_token:
        g.current_api_token = api_token

    return Tenant.from_api_token(api_token)


def get_user_from_request() -> Optional[User]:
    expire = session.get('expire')
    if not expire:
        return None

    try:
        expire = datetime.utcfromtimestamp(expire).replace(tzinfo=timezone.utc)
    except Exception:
        current_app.logger.exception('invalid session expirey')
        del session['expire']
        return None

    if expire <= timezone.now():
        current_app.logger.info('session expired')
        del session['expire']
        return None

    try:
        uid = session['uid']
    except KeyError:
        current_app.logger.error('missing uid session key', exc_info=True)
        del session['expire']
        return None

    return User.query.get(uid)


def login_user(user_id: str, session=session, current_datetime=None):
    session['uid'] = str(user_id)
    session['expire'] = int((
        (current_datetime or timezone.now()) + current_app.config['PERMANENT_SESSION_LIFETIME']).strftime('%s'))
    session.permanent = True


def logout():
    session.clear()
    g.current_user = None
    g.current_tenant = None


def get_current_user() -> Optional[User]:
    rv = getattr(g, 'current_user', None)
    if not rv:
        rv = get_user_from_request()
        g.current_user = rv
    return rv


def get_tenant_from_request():
    tenant = get_tenant_from_token()
    if tenant:
        return tenant

    user = get_current_user()
    return Tenant.from_user(user)


def set_current_tenant(tenant: Tenant):
    current_app.logger.info('Binding tenant as %r', tenant)
    g.current_tenant = tenant


def get_current_tenant() -> Tenant:
    rv = getattr(g, 'current_tenant', None)
    if rv is None:
        rv = get_tenant_from_request()
        set_current_tenant(rv)
    return rv


def generate_token(tenant: Tenant) -> str:
    s = JSONWebSignatureSerializer(current_app.secret_key, salt='auth')
    payload = {
        'repo_ids': [str(o) for o in tenant.repository_ids],
    }
    if session.get('uid'):
        payload['uid'] = str(session['uid'])
    return s.dumps(payload)


def parse_token(token: str) -> str:
    s = JSONWebSignatureSerializer(current_app.secret_key, salt='auth')
    try:
        return s.loads(token)
    except BadSignature:
        return None


def is_safe_url(target: str) -> bool:
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (
        # same scheme
        test_url.scheme in ('http', 'https') and
        # same host and port
        ref_url.netloc == test_url.netloc and
        # and different endoint
        ref_url.path != test_url.path
    )


def get_redirect_target(clear=True) -> str:
    if clear:
        session_target = session.pop('next', None)
    else:
        session_target = session.get('next')

    for target in request.values.get('next'), session_target:
        if not target:
            continue
        if is_safe_url(target):
            return target


def bind_redirect_target(target: str=None):
    if not target:
        target = request.values.get('next') or request.referrer
    if target and is_safe_url(target):
        session['next'] = target
    else:
        session.pop('next', None)
