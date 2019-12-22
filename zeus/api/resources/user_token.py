from sqlalchemy.exc import IntegrityError

from zeus import auth
from zeus.config import db
from zeus.models import UserApiToken

from .base import Resource
from ..schemas import TokenSchema

token_schema = TokenSchema()


class UserTokenResource(Resource):
    def get(self):
        """
        Return the API token for the user.
        """
        user = auth.get_current_user()
        if not user:
            return self.error("not authenticated", 401)

        token = UserApiToken.query.filter(UserApiToken.user == user).one_or_none()

        return self.respond_with_schema(token_schema, token)

    def post(self):
        """
        Create a new API token for the user.
        """
        user = auth.get_current_user()
        if not user:
            return self.error("not authenticated", 401)

        token = UserApiToken.query.filter(UserApiToken.user == user).one_or_none()

        if token:
            token.key = UserApiToken.generate_token()
        else:
            token = UserApiToken(user=user)

        try:
            db.session.add(token)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return self.respond(status=422)

        return self.respond_with_schema(token_schema, token)
