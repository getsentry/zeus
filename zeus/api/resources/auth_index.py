import json

from zeus import auth
from zeus.api import client
from zeus.exceptions import ApiError
from zeus.models import Email, Identity

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
        try:
            user_response = client.get('/users/me')
        except ApiError as exc:
            if exc.code == 401:
                return {
                    'isAuthenticated': False,
                }

        identity_list = list(Identity.query.filter(
            Identity.user_id == user_response.data['id'],
        ))

        email_list = list(Email.query.filter(
            Email.user_id == user_response.data['id'],
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
