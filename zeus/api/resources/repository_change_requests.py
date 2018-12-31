from flask import request
from marshmallow import fields, pre_dump
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from zeus import auth
from zeus.config import db
from zeus.models import Author, ChangeRequest, Email, Repository
from zeus.utils.builds import fetch_builds_for_revisions

from .base_repository import BaseRepositoryResource
from ..schemas import BuildSchema, ChangeRequestSchema, ChangeRequestCreateSchema


class ChangeRequestWithBuildSchema(ChangeRequestSchema):
    latest_build = fields.Nested(
        BuildSchema(exclude=["repository"]), dump_only=True, required=False
    )

    @pre_dump(pass_many=True)
    def get_latest_build(self, results, many):
        if results:
            builds = dict(
                fetch_builds_for_revisions(
                    self.context["repository"], [d.head_revision_sha for d in results]
                )
            )
            for item in results:
                item.latest_build = builds.get(item.head_revision_sha)
        return results


class RepositoryChangeRequestsResource(BaseRepositoryResource):
    def select_resource_for_update(self):
        return False

    def get(self, repo: Repository):
        """
        Return a list of builds for the given repository.
        """
        user = auth.get_current_user()

        query = (
            ChangeRequest.query.options(
                joinedload("head_revision"),
                joinedload("parent_revision", innerjoin=True),
                joinedload("author"),
            )
            .filter(ChangeRequest.repository_id == repo.id)
            .order_by(ChangeRequest.number.desc())
        )
        show = request.args.get("show")
        if show == "mine":
            query = query.filter(
                ChangeRequest.author_id.in_(
                    db.session.query(Author.id).filter(
                        Author.email.in_(
                            db.session.query(Email.email).filter(
                                Email.user_id == user.id
                            )
                        )
                    )
                )
            )

        schema = ChangeRequestWithBuildSchema(
            many=True, strict=True, context={"repository": repo}
        )
        return self.paginate_with_schema(schema, query)

    def post(self, repo: Repository):
        """
        Create a new change request.
        """
        schema = ChangeRequestCreateSchema(strict=True, context={"repository": repo})
        result = self.schema_from_request(schema)
        if result.errors:
            return self.respond(result.errors, 403)

        cr = result.data
        cr.repository = repo

        try:
            db.session.add(cr)
            db.session.commit()
        except IntegrityError:
            raise

            db.session.rollback()
            return self.respond(status=422)

        schema = ChangeRequestSchema(strict=True)
        return self.respond_with_schema(schema, cr, status=201)
