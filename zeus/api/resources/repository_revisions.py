from flask import request, current_app
from marshmallow import fields
from sqlalchemy.orm import joinedload
from typing import Tuple

from zeus.models import Repository, Revision
from zeus.utils.builds import fetch_builds_for_revisions

from .base_repository import BaseRepositoryResource
from ..schemas import BuildSchema, RevisionSchema


class RevisionWithBuildSchema(RevisionSchema):
    latest_build = fields.Nested(
        BuildSchema(exclude=["repository"]), dump_only=True, required=False
    )


revisions_schema = RevisionWithBuildSchema(many=True, strict=True)


class RepositoryRevisionsResource(BaseRepositoryResource):

    def fetch_revisions(
        self, repo: Repository, page: int, parent: str = None
    ) -> Tuple[list, bool]:
        if current_app.config.get("MOCK_REVISIONS"):
            return Revision.query.filter(Revision.repository_id == repo.id).order_by(
                Revision.date_created.desc()
            ).all()

        vcs = repo.get_vcs()
        if not vcs:
            return []

        per_page = min(int(request.args.get("per_page", 50)), 50)
        branch = request.args.get("branch")
        if not parent and branch is None:
            branch = vcs.get_default_branch()

        vcs_log = list(
            vcs.log(
                limit=per_page + 1,
                offset=(page - 1) * per_page,
                parent=parent,
                branch=branch,
            )
        )

        if not vcs_log:
            return [], False

        has_more = len(vcs_log) > per_page
        vcs_log = vcs_log[:per_page]

        existing = Revision.query.options(joinedload("author")).filter(
            Revision.repository_id == repo.id, Revision.sha.in_(c.sha for c in vcs_log)
        )

        revisions_map = {r.sha: r for r in existing}
        return [revisions_map.get(item.sha, item) for item in vcs_log], has_more

    def get(self, repo: Repository):
        """
        Return a list of revisions for the given repository.
        """
        page = int(request.args.get("page", 1))
        if not (page > 0):
            page = 1

        parent = request.args.get("parent")

        revisions, has_more = self.fetch_revisions(repo, page, parent=parent)
        if revisions:
            builds = dict(fetch_builds_for_revisions(repo, revisions))
            for revision in revisions:
                revision.latest_build = builds.get(revision.sha)

        if not parent:
            base_url = self.build_base_url(without=["page", "parent"])
            if page == 1:
                base_url += "&parent={}".format(revisions[0].sha)
            else:
                base_url += "&parent=head"
        else:
            base_url = None

        response = self.respond_with_schema(revisions_schema, revisions)
        return self.build_paged_response(
            response,
            page + 1 if has_more else None,
            page - 1 if page > 1 else None,
            base_url=base_url,
        )
