from flask import request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from zeus import auth
from zeus.config import db
from zeus.models import Author, ChangeRequest, Email, Repository

from .base_repository import BaseRepositoryResource
from ..schemas import ChangeRequestSchema, ChangeRequestCreateSchema

change_requests_schema = ChangeRequestSchema(many=True, strict=True)


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
                joinedload("parent_revision"),
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

        return self.paginate_with_schema(change_requests_schema, query)

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
