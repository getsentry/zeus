from flask import request
from sqlalchemy.orm import joinedload

from zeus.models import Repository, Revision

from .base_repository import BaseRepositoryResource
from ..schemas import RevisionSchema

revisions_schema = RevisionSchema(many=True, strict=True)


class RepositoryRevisionsResource(BaseRepositoryResource):
    def get(self, repo: Repository):
        """
        Return a list of revisions for the given repository.
        """
        vcs = repo.get_vcs()
        if not vcs:
            return self.respond([])

        vcs.ensure()

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

        return self.respond_with_schema(revisions_schema, revisions)
