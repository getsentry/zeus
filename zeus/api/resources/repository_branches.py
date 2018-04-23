import json

from zeus.config import redis
from zeus.models import Repository

from .base_repository import BaseRepositoryResource


class RepositoryBranchesResource(BaseRepositoryResource):
    cache_key = "api:1:repobranches:{repo_id}"
    cache_expire = 60

    def get(self, repo: Repository):
        """
        Return a list of revisions for the given repository.
        """
        cache_key = self.cache_key.format(repo_id=repo.id.hex)

        result = redis.get(cache_key)
        if result is None:
            vcs = repo.get_vcs()
            if not vcs:
                return self.respond([])

            vcs.ensure()
            result = vcs.get_known_branches()
            redis.setex(cache_key, json.dumps(result), self.cache_expire)
        else:
            result = json.loads(result)

        return self.respond([{"name": r} for r in result])
