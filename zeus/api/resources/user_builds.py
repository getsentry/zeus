from sqlalchemy.orm import contains_eager, joinedload, subqueryload_all

from zeus import auth
from zeus.config import db
from zeus.models import Author, Build, Email, Source, User

from .base import Resource
from ..schemas import BuildSchema

builds_schema = BuildSchema(many=True, strict=True)


class UserBuildsResource(Resource):
    def get(self, user_id):
        """
        Return a list of builds for the given user.
        """
        if user_id == 'me':
            user = auth.get_current_user()
            if not user:
                return self.error('not authenticated', 401)
        else:
            user = User.query.get(user_id)

        query = Build.query.options(
            joinedload('repository'),
            contains_eager('source'),
            joinedload('source').joinedload('author'),
            joinedload('source').joinedload('revision'),
            joinedload('source').joinedload('patch'),
            subqueryload_all('stats'),
        ).join(
            Source,
            Build.source_id == Source.id,
        ).filter(
            Source.author_id.in_(db.session.query(Author.id).filter(Author.email.in_(
                db.session.query(Email.email).filter(
                    Email.user_id == user.id
                )
            )))
        ).order_by(Build.number.desc())
        return self.paginate_with_schema(builds_schema, query)
