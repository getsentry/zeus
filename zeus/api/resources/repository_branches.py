from zeus.models import Repository
from zeus.vcs import vcs_client

from .base_repository import BaseRepositoryResource


class RepositoryBranchesResource(BaseRepositoryResource):
    cache_key = "api:1:repobranches:{repo_id}"
    cache_expire = 60

    def get(self, repo: Repository):
        """
        Return a list of revisions for the given repository.
        """
        result = vcs_client.branches(repo.id)

        return self.respond([{"name": r} for r in result])
