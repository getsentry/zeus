from flask import request
from marshmallow import fields
from sqlalchemy.orm import contains_eager, joinedload, subqueryload_all

from zeus.models import Build, Repository, Revision, Source

from .base_repository import BaseRepositoryResource
from ..schemas import BuildSchema, RevisionSchema


class RevisionWithBuildSchema(RevisionSchema):
    latest_build = fields.Nested(BuildSchema(), dump_only=True, required=False)


revisions_schema = RevisionWithBuildSchema(many=True, strict=True)


class RepositoryRevisionsResource(BaseRepositoryResource):
    def get(self, repo: Repository):
        """
        Return a list of revisions for the given repository.
        """
        vcs = repo.get_vcs()
        if not vcs:
            return self.respond([])

        vcs.ensure(update_if_exists=False)

        branch = request.args.get('branch', vcs.get_default_branch())
        parent = request.args.get('parent')

        vcs_log = list(vcs.log(
            limit=50,
            parent=parent,
            branch=branch,
        ))
        if vcs_log:
            revisions_map = {
                r.sha: r
                for r in Revision.query.options(
                    joinedload('author'),
                ).filter(
                    Revision.repository_id == repo.id,
                    Revision.sha.in_(c.sha for c in vcs_log)
                )
            }

            revisions = []
            for item in vcs_log:
                if item.sha in revisions_map:
                    result = revisions_map[item.sha]
                else:
                    result = item
                revisions.append(result)
        else:
            revisions = []

        if revisions:
            # we query extra builds here, but its a lot easier than trying to get
            # sqlalchemy to do a ``select (subquery)`` clause and maintain tenant
            # constraints
            builds = {
                b.source.revision_sha: b
                for b in Build.query.options(
                    contains_eager('source'),
                    joinedload('source').joinedload('author'),
                    joinedload('source').joinedload('revision'),
                    joinedload('source').joinedload('patch'),
                    subqueryload_all('stats'),
                ).join(
                    Source,
                    Build.source_id == Source.id,
                ).filter(
                    Build.repository_id == repo.id,
                    Source.repository_id == repo.id,
                    Source.revision_sha.in_([r.sha for r in revisions]),
                    Source.patch_id == None,  # NOQA
                ).order_by(Build.number.asc())
            }
            for revision in revisions:
                revision.latest_build = builds.get(revision.sha)

        return self.respond_with_schema(revisions_schema, revisions)
