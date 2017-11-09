from flask import request, current_app
from marshmallow import fields
from sqlalchemy.orm import joinedload

from zeus.models import Repository, Revision
from zeus.utils.builds import fetch_builds_for_revisions

from .base_repository import BaseRepositoryResource
from ..schemas import BuildSchema, RevisionSchema


class RevisionWithBuildSchema(RevisionSchema):
    latest_build = fields.Nested(BuildSchema(), dump_only=True, required=False)


revisions_schema = RevisionWithBuildSchema(many=True, strict=True)


class RepositoryRevisionsResource(BaseRepositoryResource):
    def fetch_revisions(self, repo: Repository):
        if current_app.config.get('MOCK_REVISIONS'):
            return Revision.query \
                .filter(Revision.repository_id == repo.id) \
                .order_by(Revision.date_created.desc()) \
                .all()

        vcs = repo.get_vcs()
        if not vcs:
            return []

        vcs.ensure(update_if_exists=False)
        branch = request.args.get('branch', vcs.get_default_branch())
        parent = request.args.get('parent')

        vcs_log = list(vcs.log(
            limit=50,
            parent=parent,
            branch=branch,
        ))

        if not vcs_log:
            return []

        existing = Revision.query \
            .options(joinedload('author')) \
            .filter(
                Revision.repository_id == repo.id,
                Revision.sha.in_(c.sha for c in vcs_log)
            )

        revisions_map = {r.sha: r for r in existing}
        return [revisions_map.get(item.sha, item) for item in vcs_log]

    def get(self, repo: Repository):
        """
        Return a list of revisions for the given repository.
        """
        revisions = self.fetch_revisions(repo)
        if revisions:
            builds = dict(fetch_builds_for_revisions(repo, revisions))
            for revision in revisions:
                revision.latest_build = builds.get(revision.sha)

        return self.respond_with_schema(revisions_schema, revisions)
