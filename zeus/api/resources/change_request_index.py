from flask import request
from marshmallow import fields, pre_dump
from sqlalchemy.orm import joinedload, subqueryload_all

from zeus import auth
from zeus.config import db
from zeus.models import Author, ChangeRequest, Email, Repository, User
from zeus.utils.builds import fetch_builds_for_revisions

from .base import Resource
from ..schemas import BuildSchema, ChangeRequestSchema


class ChangeRequestWithBuildSchema(ChangeRequestSchema):
    latest_build = fields.Nested(
        BuildSchema(exclude=["id", "repository"]), dump_only=True, required=False
    )

    @pre_dump(pass_many=True)
    def get_latest_build(self, results, many, **kwargs):
        if results:
            builds = dict(
                fetch_builds_for_revisions(
                    [d.head_revision for d in results if d.head_revision]
                )
            )
            for item in results:
                item.latest_build = builds.get(
                    (item.repository_id, item.head_revision_sha)
                )
        return results


class ChangeRequestIndexResource(Resource):
    def select_resource_for_update(self):
        return False

    def get(self):
        """
        Return a list of change requests.
        """
        tenant = auth.get_current_tenant()
        if not tenant.repository_ids:
            return self.respond([])

        query = (
            ChangeRequest.query.options(
                joinedload("head_revision"),
                joinedload("parent_revision"),
                subqueryload_all("authors"),
            )
            .filter(ChangeRequest.repository_id.in_(tenant.repository_ids))
            .order_by(ChangeRequest.date_created.desc())
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
                ChangeRequest.author_id.in_(
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
            query = query.filter(ChangeRequest.repository_id == repo.id)

        schema = ChangeRequestWithBuildSchema(many=True)
        return self.paginate_with_schema(schema, query)
