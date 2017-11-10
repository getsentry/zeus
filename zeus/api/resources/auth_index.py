from flask import session

from zeus import auth
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
            user = User.query.get(session['uid'])
            if user is None:
                session.clear()
        else:
            user = None

        if user is None:
            context = {
                'isAuthenticated': False,
            }
        else:
            identity_list = list(Identity.query.filter(
                Identity.user_id == user.id,
            ))

            email_list = list(Email.query.filter(
                Email.user_id == user.id,
            ))

            context = {
                'isAuthenticated': True,
                'user': user_schema.dump(user).data,
                'emails': emails_schema.dump(email_list).data,
                'identities': identities_schema.dump(identity_list).data,
            }
        return context

    def delete(self):
        """
        Logout.
        """
        auth.logout()

        return {
            'isAuthenticated': False,
            'user': None,
        }
