from __future__ import absolute_import, division, unicode_literals

from flask import session
from zeus.models import User

from .base import Resource
from ..schemas import UserSchema


class AuthIndexResource(Resource):
    def get(self):
        """
        Return information on the currently authenticated user.
        """
        if session.get('uid'):
            user = User.query.get(session['uid'])
            if user is None:
                del session['uid']
        else:
            user = None

        if user is None:
            context = {
                'isAuthenticated': False,
                'user': None,
            }
        else:
            context = {
                'isAuthenticated': True,
                'user': UserSchema(strict=True).dump(user).data,
            }
        return context