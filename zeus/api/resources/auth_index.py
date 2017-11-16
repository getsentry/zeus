import json

from flask import session
from sqlalchemy.orm import subqueryload_all

from zeus import auth
from zeus.api import client
from zeus.models import Email, Identity, User

from .base import Resource
from ..schemas import EmailSchema, IdentitySchema, UserSchema

emails_schema = EmailSchema(many=True, strict=True)
identities_schema = IdentitySchema(many=True, strict=True)
user_schema = UserSchema(strict=True)


class AuthIndexResource(Resource):
    auth_required = False

    def get(self):
        """
        Return information on the currently authenticated user.
        """
        if session.get('uid'):
            user = User.query.options(
                subqueryload_all('options')
            ).get(session['uid'])
            if user is None:
                session.clear()
        else:
            user = None

        if user is None:
            return {
                'isAuthenticated': False,
            }

        user_response = client.get('/users/me')

        identity_list = list(Identity.query.filter(
            Identity.user_id == user.id,
        ))

        email_list = list(Email.query.filter(
            Email.user_id == user.id,
        ))

        return {
            'isAuthenticated': True,
            'user': json.loads(user_response.data),
            'emails': emails_schema.dump(email_list).data,
            'identities': identities_schema.dump(identity_list).data,
        }

    def delete(self):
        """
        Logout.
        """
        auth.logout()

        return {
            'isAuthenticated': False,
            'user': None,
        }
