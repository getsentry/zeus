from typing import List

from zeus.models import Repository, User
from zeus.utils.ssh import KeyPair


# this API is very much a work in progress, and hasn't yet had a lot of thought put
# into it
class RepositoryProvider(object):
    def __init__(self, cache=True):
        self.cache = cache

    def get_owners(self, user: User) -> List[dict]:
        raise NotImplementedError

    def get_repos_for_owner(self, user: User, owner_name: str) -> List[dict]:
        raise NotImplementedError

    def get_repo(self, user: User, owner_name: str, repo_name: str) -> dict:
        raise NotImplementedError

    def add_key(self, user: User, owner_name: str, repo_name: str, key: KeyPair):
        raise NotImplementedError

    def has_access(self, repository: Repository, user: User) -> bool:
        raise NotImplementedError
