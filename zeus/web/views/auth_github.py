import zeus

from flask import current_app, redirect, request, url_for
from flask.views import MethodView
from oauth2client.client import FlowExchangeError, OAuth2WebServerFlow
from sqlalchemy.exc import IntegrityError

from zeus import auth
from zeus.config import db
from zeus.constants import GITHUB_AUTH_URI, GITHUB_TOKEN_URI
from zeus.models import (
    Email, Identity, Repository, RepositoryAccess, RepositoryProvider, User
)
from zeus.utils.github import GitHubClient
from zeus.vcs.providers.github import GitHubRepositoryProvider


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
        auth.bind_redirect_target()
        redirect_uri = url_for(self.authorized_url, _external=True)
        flow = get_auth_flow(redirect_uri=redirect_uri, scopes=self.scopes)
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)


class GitHubCompleteView(MethodView):
    # TODO(dcramer): we dont handle the case where the User row has been deleted,
    # but the identity still exists. It shouldn't happen.
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
            'login': user_data['login'],
        }

        email_list = github.get('/user/emails')
        email_list.append({
            'email': '{}@users.noreply.github.com'.format(user_data['login']),
            'verified': True,
        })

        primary_email = user_data.get('email')
        # HACK(dcramer): capture github's anonymous email addresses when they're not listed
        # (we haven't actually confirmed they're not listed)
        if not primary_email:
            primary_email = next((
                e['email'] for e in email_list
                if e['verified'] and e['primary']
            ))

        try:
            # we first attempt to create a new user + identity
            with db.session.begin_nested():
                user = User(
                    email=primary_email,
                )
                db.session.add(user)
                identity = Identity(
                    user=user,
                    external_id=str(user_data['id']),
                    provider='github',
                    scopes=scopes,
                    config=identity_config,
                )
                db.session.add(identity)
            user_id = user.id
        except IntegrityError:
            # if that fails, assume the identity exists
            identity = Identity.query.filter(
                Identity.external_id == str(user_data['id']),
                Identity.provider == 'github',
            ).first()

            # and if it doesnt, attempt to find a matching user,
            # as it means the failure above was due to that
            if not identity:
                user = User.query.filter(
                    User.email == primary_email
                ).first()
                assert user  # this should not be possible unless we've got a race condition
                identity = Identity(
                    user=user,
                    external_id=str(user_data['id']),
                    provider='github',
                    scopes=scopes,
                    config=identity_config,
                )
                db.session.add(identity)
                user_id = user.id
            else:
                identity.config = identity_config
                identity.scopes = scopes
                db.session.add(identity)
                user_id = identity.user_id

        db.session.flush()

        for email in email_list:
            try:
                with db.session.begin_nested():
                    db.session.add(Email(
                        user_id=user_id,
                        email=email['email'],
                        verified=email['verified'],
                    ))
            except IntegrityError:
                pass

        db.session.commit()

        # forcefully expire a session after permanent_session_lifetime
        # Note: this is enforced in zeus.auth
        auth.login_user(user_id)

        # now lets try to update the repos they have access to based on whats
        # enabled
        user = auth.get_current_user()
        grant_access_to_existing_repos(user)

        return redirect(auth.get_redirect_target(clear=True) or '/')


def grant_access_to_existing_repos(user):
    provider = GitHubRepositoryProvider(cache=True)
    owner_list = [o['name'] for o in provider.get_owners(user)]
    if owner_list:
        matching_repos = Repository.query.unrestricted_unsafe().filter(
            Repository.provider == RepositoryProvider.github,
            Repository.owner_name.in_(owner_list),
            ~Repository.id.in_(db.session.query(
                RepositoryAccess.repository_id,
            ).filter(
                RepositoryAccess.user_id == user.id,
            ))
        )
        for repo in matching_repos:
            if provider.has_access(auth.get_current_user(), repo):
                try:
                    with db.session.begin_nested():
                        db.session.add(RepositoryAccess(
                            repository_id=repo.id,
                            user_id=user.id,
                        ))
                        db.session.flush()
                except IntegrityError:
                    pass
            db.session.commit()
