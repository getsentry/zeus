from flask import session

from zeus import auth
from zeus.models import Identity, User

from .base import Resource
from ..schemas import IdentitySchema, UserSchema

user_schema = UserSchema(strict=True)
identities_schema = IdentitySchema(many=True, strict=True)


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
                'user': None,
                'identities': [],
            }
        else:
            identity_list = list(Identity.query.filter(
                Identity.user_id == User.id,
            ))

            context = {
                'isAuthenticated': True,
                'user': user_schema.dump(user).data,
                'identities': identities_schema.dump(identity_list).data,
            }
        return context

    def delete(self):
        """
        Logout.
        """
        if not session.get('uid'):
            return

        auth.logout()

        return {
            'isAuthenticated': False,
            'user': None,
        }
