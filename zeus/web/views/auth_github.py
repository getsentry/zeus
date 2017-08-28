import zeus

from flask import current_app, redirect, request, url_for
from flask.views import MethodView
from oauth2client.client import FlowExchangeError, OAuth2WebServerFlow
from sqlalchemy.exc import IntegrityError

from zeus import auth
from zeus.config import db
from zeus.constants import GITHUB_AUTH_URI, GITHUB_TOKEN_URI
from zeus.models import Identity, User
from zeus.utils.github import GitHubClient


def get_auth_flow(redirect_uri=None, scopes=('user:email', )):
    # XXX(dcramer): we have to generate this each request because oauth2client
    # doesn't want you to set redirect_uri as part of the request, which causes
    # a lot of runtime issues.
    return OAuth2WebServerFlow(
        client_id=current_app.config['GITHUB_CLIENT_ID'],
        client_secret=current_app.config['GITHUB_CLIENT_SECRET'],
        scope=','.join(scopes),
        redirect_uri=redirect_uri,
        user_agent='zeus/{0}'.format(
            zeus.VERSION,
        ),
        auth_uri=GITHUB_AUTH_URI,
        token_uri=GITHUB_TOKEN_URI,
    )


class GitHubAuthView(MethodView):
    def __init__(self, authorized_url, scopes=('user:email', )):
        self.authorized_url = authorized_url
        self.scopes = scopes
        super(GitHubAuthView, self).__init__()

    def get(self):
        redirect_uri = url_for(self.authorized_url, _external=True)
        flow = get_auth_flow(redirect_uri=redirect_uri, scopes=self.scopes)
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)


class GitHubCompleteView(MethodView):
    def __init__(self, complete_url):
        self.complete_url = complete_url
        super(GitHubCompleteView, self).__init__()

    def get(self):
        redirect_uri = request.url
        flow = get_auth_flow(redirect_uri=redirect_uri)
        try:
            oauth_response = flow.step2_exchange(request.args['code'])
        except FlowExchangeError:
            return redirect('/?auth_error=true')

        scopes = oauth_response.token_response['scope'].split(',')

        if 'user:email' not in scopes:
            raise NotImplementedError

        # fetch user details
        github = GitHubClient(token=oauth_response.access_token)
        user_data = github.get('/user')

        identity_config = {
            'access_token': oauth_response.access_token,
            'refresh_token': oauth_response.refresh_token,
            'scopes': scopes,
            'login': user_data['login'],
        }

        email = user_data.get('email')
        # no primary/public email specified
        if not email:
            emails = github.get('/user/emails')
            email = next((
                e['email'] for e in emails
                if e['verified'] and e['primary']
            ))
        try:
            with db.session.begin_nested():
                user = User(
                    email=email,
                )
                db.session.add(user)
                identity = Identity(
                    user=user,
                    external_id=str(user_data['id']),
                    provider='github',
                    config=identity_config,
                )
                db.session.add(identity)
            user_id = user.id
        except IntegrityError:
            identity = Identity.query.filter(
                Identity.external_id == str(user_data['id']),
                Identity.provider == 'github',
            ).first()
            identity.config = identity_config
            db.session.add(identity)
            user_id = identity.user_id

        db.session.commit()

        # forcefully expire a session after permanent_session_lifetime
        # Note: this is enforced in zeus.auth
        auth.login_user(user_id)

        return redirect(url_for(self.complete_url))
