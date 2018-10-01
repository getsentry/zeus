from sqlalchemy.orm import joinedload, subqueryload_all

from zeus import auth
from zeus.config import db
from zeus.models import Author, Build, Email, User

from .base import Resource
from ..schemas import BuildSchema

builds_schema = BuildSchema(many=True, strict=True)


class UserBuildsResource(Resource):
    def get(self, user_id):
        """
        Return a list of builds for the given user.
        """
        if user_id == "me":
            user = auth.get_current_user()
            if not user:
                return self.error("not authenticated", 401)

        else:
            user = User.query.get(user_id)

        query = (
            Build.query.options(
                joinedload("repository"),
                joinedload("source", innerjoin=True),
                joinedload("source", innerjoin=True).joinedload(
                    "author", innerjoin=True
                ),
                joinedload("source", innerjoin=True).joinedload(
                    "revision", innerjoin=True
                ),
                subqueryload_all("stats"),
            )
            .filter(
                Build.author_id.in_(
                    db.session.query(Author.id).filter(
                        Author.email.in_(
                            db.session.query(Email.email).filter(
                                Email.user_id == user.id, Email.verified == True  # NOQA
                            )
                        )
                    )
                )
            )
            .order_by(Build.date_created.desc())
        )
        return self.paginate_with_schema(builds_schema, query)
