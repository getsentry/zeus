import zeus
import sys

from flask import current_app, redirect, request, session, url_for
from flask.views import MethodView
from oauth2client.client import OAuth2WebServerFlow

from zeus.db.utils import get_or_create
from zeus.models import User

GITHUB_AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
GITHUB_REVOKE_URI = 'https://accounts.google.com/o/oauth2/revoke'
GITHUB_TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'


def get_auth_flow(redirect_uri=None, scopes=()):
    # XXX(dcramer): we have to generate this each request because oauth2client
    # doesn't want you to set redirect_uri as part of the request, which causes
    # a lot of runtime issues.
    return OAuth2WebServerFlow(
        client_id=current_app.config['GITHUB_CLIENT_ID'],
        client_secret=current_app.config['GITHUB_CLIENT_SECRET'],
        scope=' '.join(scopes),
        redirect_uri=redirect_uri,
        user_agent='zeus/{0} (python {1})'.format(
            zeus.VERSION,
            sys.version,
        ),
        auth_uri=GITHUB_AUTH_URI,
        token_uri=GITHUB_TOKEN_URI,
        revoke_uri=GITHUB_REVOKE_URI,
    )


class GitHubLoginView(MethodView):
    def __init__(self, authorized_url):
        self.authorized_url = authorized_url
        super(GitHubLoginView, self).__init__()

    def get(self):
        redirect_uri = url_for(self.authorized_url, _external=True)
        flow = get_auth_flow(redirect_uri=redirect_uri)
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)


class GitHubCompleteView(MethodView):
    def __init__(self, complete_url, authorized_url):
        self.complete_url = complete_url
        self.authorized_url = authorized_url
        super(GitHubCompleteView, self).__init__()

    def get(self):
        redirect_uri = url_for(self.authorized_url, _external=True)
        flow = get_auth_flow(redirect_uri=redirect_uri)
        resp = flow.step2_exchange(request.args['code'])

        user, _ = get_or_create(User, where={
            'email': resp.id_token['email'],
        })

        identity, _ = get_or_create(Identity, where={
            'user_id': user.id,
            'provider': 'github',
            'defaults': {
                'access_token': resp.access_token,
            }
        })

        session['uid'] = user.id.hex

        return redirect(url_for(self.complete_url))
