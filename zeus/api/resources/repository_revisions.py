from flask import request, current_app
from marshmallow import fields, pre_dump
from sqlalchemy.orm import subqueryload_all
from typing import Optional, Tuple

from zeus.config import nplusone
from zeus.models import Repository, Revision
from zeus.utils.builds import fetch_builds_for_revisions
from zeus.vcs import vcs_client

from .base_repository import BaseRepositoryResource
from ..schemas import BuildSchema, RevisionSchema


class RevisionWithBuildSchema(RevisionSchema):
    latest_build = fields.Nested(
        BuildSchema(exclude=["repository", "id"]), dump_only=True, required=False
    )

    @pre_dump(pass_many=True)
    def get_latest_build(self, results, many, **kwargs):
        if results:
            with nplusone.ignore("eager_load"):
                builds = dict(fetch_builds_for_revisions(results))
            for item in results:
                item.latest_build = builds.get((item.repository_id, item.sha))
        return results


revisions_schema = RevisionWithBuildSchema(many=True)


class RepositoryRevisionsResource(BaseRepositoryResource):
    def fetch_revisions(
        self, repo: Repository, page: int, parent: str = None
    ) -> Tuple[list, bool]:
        per_page = min(int(request.args.get("per_page", 50)), 50)

        if current_app.config.get("MOCK_REVISIONS"):
            results = (
                Revision.query.filter(Revision.repository_id == repo.id)
                .order_by(Revision.date_created.desc())
                .offset((page - 1) * per_page)
                .limit(per_page + 1)
                .all()
            )
            has_more = len(results) > per_page
            return results[:per_page], has_more

        branch = request.args.get("branch")
        if not parent and branch is None:
            branch = "!default"

        vcs_log = list(
            vcs_client.log(
                repo.id,
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

        existing = Revision.query.options(subqueryload_all("authors")).filter(
            Revision.repository_id == repo.id,
            Revision.sha.in_(c["sha"] for c in vcs_log),
        )

        revisions_map = {r.sha: r for r in existing}
        results = []
        for item in vcs_log:
            # XXX(dcramer): technically its possible for the vcs server to be out of sync with the database
            if item["sha"] in revisions_map:
                results.append(revisions_map[item["sha"]])
        return results, has_more

    def get(self, repo: Repository):
        """
        Return a list of revisions for the given repository.
        """
        page = int(request.args.get("page", 1))
        if not (page > 0):
            page = 1

        parent = request.args.get("parent")

        revisions, has_more = self.fetch_revisions(repo, page, parent=parent)

        base_url: Optional[str] = None
        if not parent:
            base_url = self.build_base_url(without=["page", "parent"])
            if page == 1 and revisions:
                base_url += "&parent={}".format(revisions[0].sha)
            else:
                base_url += "&parent=head"

        response = self.respond_with_schema(revisions_schema, revisions)
        return self.build_paged_response(
            response,
            page + 1 if has_more else None,
            page - 1 if page > 1 else None,
            base_url=base_url,
        )
