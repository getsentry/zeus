from flask import redirect, request, url_for
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from zeus import auth
from zeus.config import db, github
from zeus.constants import GITHUB_DEFAULT_SCOPES
from zeus.models import (
    Email, Identity, User
)
from zeus.tasks import sync_github_access
from zeus.utils.github import GitHubClient


class GitHubAuthView(MethodView):
    def __init__(self, authorized_url, scopes=GITHUB_DEFAULT_SCOPES):
        self.authorized_url = authorized_url
        self.scopes = scopes
        super(GitHubAuthView, self).__init__()

    def get(self):
        auth.bind_redirect_target()
        return github.authorize(
            callback=url_for(self.authorized_url, _external=True),
            scope=','.join(self.scopes),
            access_type='offline',
        )


class GitHubCompleteView(MethodView):
    # TODO(dcramer): we dont handle the case where the User row has been deleted,
    # but the identity still exists. It shouldn't happen.
    def get(self):
        resp = github.authorized_response()
        if resp is None or resp.get('access_token') is None:
            return 'Access denied: reason=%s error=%s resp=%s' % (
                request.args['error'],
                request.args['error_description'],
                resp
            )

        scopes = resp['scope'].split(',')

        if 'user:email' not in scopes:
            raise NotImplementedError

        # fetch user details
        client = GitHubClient(token=resp['access_token'])
        user_data = client.get('/user')

        identity_config = {
            'access_token': resp['access_token'],
            'refresh_token': resp.get('refresh_token'),
            'login': user_data['login'],
        }

        email_list = client.get('/user/emails')
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
            new_user = True
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
            new_user = False
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

        user = auth.get_current_user()
        if new_user:
            # update synchronously so the new user has a better experience
            sync_github_access(user_id=user.id)
        else:
            sync_github_access.delay(user_id=user.id)

        return redirect(auth.get_redirect_target(clear=True) or '/')
