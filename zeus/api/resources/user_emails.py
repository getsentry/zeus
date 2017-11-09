from zeus import auth
from zeus.models import Email

from .base import Resource
from ..schemas import EmailSchema

emails_schema = EmailSchema(many=True, strict=True)


class UserEmailsResource(Resource):
    def get(self, user_id):
        """
        Return a list of builds for the given user.
        """
        if user_id == 'me':
            user = auth.get_current_user()
            if not user:
                return self.error('not authenticated', 401)
        else:
            raise NotImplementedError

        query = Email.query.filter(
            Email.user_id == user.id,
        ).order_by(Email.email.asc())
        return self.paginate_with_schema(emails_schema, query)
