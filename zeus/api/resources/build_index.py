from flask import request
from sqlalchemy.orm import joinedload, subqueryload_all

from zeus import auth
from zeus.config import db
from zeus.models import Author, Build, Email, Repository, User

from .base import Resource
from ..schemas import BuildSchema

builds_schema = BuildSchema(many=True, strict=True)


class BuildIndexResource(Resource):
    def select_resource_for_update(self):
        return False

    def get(self):
        """
        Return a list of builds.
        """
        # tenants automatically restrict this query but we dont want
        # to include public repos
        tenant = auth.get_current_tenant()
        if not tenant.repository_ids:
            return self.respond([])

        query = (
            Build.query.options(
                joinedload("repository", innerjoin=True),
                joinedload("source", innerjoin=True),
                joinedload("source", innerjoin=True).joinedload("author"),
                joinedload("source", innerjoin=True).joinedload(
                    "revision", innerjoin=True
                ),
                subqueryload_all("stats"),
            )
            .filter(Build.repository_id.in_(tenant.repository_ids))
            .order_by(Build.date_created.desc())
        )
        user = request.args.get("user")
        if user:
            if user == "me":
                user = auth.get_current_user()
            else:
                user = User.query.get(user)
            if not user:
                return self.respond([])

            query = query.filter(
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
        repository = request.args.get("repository")
        if repository:
            repo = Repository.from_full_name(repository)
            if not repo:
                return self.respond([])
            query = query.filter(Build.repository_id == repo.id)

        return self.paginate_with_schema(builds_schema, query)
