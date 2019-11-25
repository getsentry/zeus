from marshmallow import fields, pre_dump
from sqlalchemy.exc import IntegrityError

from zeus.config import db
from zeus.models import Repository
from zeus.utils.builds import fetch_builds_for_revisions

from .base_repository import BaseRepositoryResource
from ..schemas import BuildSchema, ChangeRequestSchema, ChangeRequestCreateSchema


class ChangeRequestWithBuildSchema(ChangeRequestSchema):
    latest_build = fields.Nested(
        BuildSchema(exclude=["repository"]), dump_only=True, required=False
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
                item.latest_build = builds.get(item.head_revision_sha)
        return results


class RepositoryChangeRequestsResource(BaseRepositoryResource):
    def select_resource_for_update(self):
        return False

    def post(self, repo: Repository):
        """
        Create a new change request.
        """
        schema = ChangeRequestCreateSchema(context={"repository": repo})
        cr = self.schema_from_request(schema)
        cr.repository = repo

        try:
            db.session.add(cr)
            db.session.commit()
        except IntegrityError as exc:
            if "duplicate" in str(exc):
                db.session.rollback()
                return self.respond(status=422)
            raise

        if not cr.parent_revision_sha or (not cr.head_revision_sha and cr.head_ref):
            from zeus.tasks import resolve_ref_for_change_request

            resolve_ref_for_change_request.delay(change_request_id=cr.id)

        schema = ChangeRequestSchema()
        return self.respond_with_schema(schema, cr, status=201)
