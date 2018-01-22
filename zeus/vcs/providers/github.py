import json

from hashlib import md5
from typing import List

from zeus.config import redis
from zeus.constants import Permission
from zeus.exceptions import ApiError, ApiUnauthorized, IdentityNeedsUpgrade
from zeus.models import Identity, Repository, User
from zeus.utils.github import GitHubClient
from zeus.utils.ssh import KeyPair

from .base import RepositoryProvider

ONE_DAY = 60 * 60 * 24


def get_github_client(user: User, scopes=()) -> GitHubClient:
    identity = Identity.query.filter(
        Identity.provider == 'github',
        Identity.user_id == user.id
    ).first()

    if not identity:
        raise ApiUnauthorized

    for scope in scopes:
        if scope not in identity.scopes:
            raise IdentityNeedsUpgrade(
                scope=scope,
                identity=identity,
            )

    return GitHubClient(token=identity.config['access_token']), identity


class GitHubRepositoryProvider(RepositoryProvider):
    def get_owners(self, user: User) -> List[dict]:
        github, identity = get_github_client(user)
        response = github.get('/user/orgs')
        return [{
            'name': r['login']
        } for r in response]

    def get_repos_for_owner(self, user: User, owner_name: str,
                            include_private_repos=False) -> List[dict]:
        if include_private_repos:
            github, identity = get_github_client(user, scopes=['repo'])
        else:
            github, identity = get_github_client(user)

        cache = GitHubCache(user=user, client=github,
                            scopes=identity.scopes)

        results = []
        for repo_data in cache.get_repos(owner_name, no_cache=not self.cache):
            owner_name, repo_name = repo_data['full_name'].split('/', 1)
            results.append({
                'id': repo_data['id'],
                'owner_name': owner_name,
                'name': repo_name,
                'admin': repo_data.get('admin', False),
                'url': repo_data['ssh_url'],
                'config': {
                    'full_name': repo_data['full_name']
                }
            })
        return results

    def get_repo(self, user: User, owner_name: str, repo_name: str) -> dict:
        github, identity = get_github_client(user)
        try:
            repo_data = github.get(
                '/repos/{}/{}'.format(owner_name, repo_name))
        except ApiError as exc:
            if exc.code == 404 and 'repo' not in identity.scopes:
                raise IdentityNeedsUpgrade(
                    scope='repo',
                    identity=identity,
                )
            raise

        owner_name, repo_name = repo_data['full_name'].split('/', 1)
        return {
            'id': repo_data['id'],
            'owner_name': owner_name,
            'name': repo_name,
            'url': repo_data['ssh_url'],
            'admin': repo_data['permissions'].get('admin', False),
            'config': {
                'full_name': repo_data['full_name']
            }
        }

    def add_key(self, user: User, owner_name: str, repo_name: str, key: KeyPair) -> dict:
        github, _ = get_github_client(user)
        github.post(
            '/repos/{}/{}/keys'.format(owner_name, repo_name),
            json={
                'title': 'zeus',
                'key': key.public_key,
                'read_only': True,
            }
        )

    def get_permission(self, user: User, repo: Repository) -> bool:
        try:
            repo = self.get_repo(user, *repo.data['full_name'].split('/', 1))
        except ApiError as exc:
            if exc.code == 404:
                return None
            raise
        return Permission.admin if repo['admin'] else Permission.read

    def has_access(self, user: User, repo: Repository) -> bool:
        try:
            self.get_repo(user, *repo.data['full_name'].split('/', 1))
        except ApiError as exc:
            if exc.code == 404:
                return False
            raise
        return True


class GitHubCache(object):
    version = 4

    def __init__(self, user: User, client: GitHubClient=None, scopes=()):
        self.user = user
        self.scopes = scopes
        if client is None:
            self.client = self.get_github_client(user)
        else:
            self.client = client

    def get_repos(self, owner, no_cache=False):
        cache_key = 'gh:{}:repos:{}:{}:{}'.format(
            self.version,
            md5(self.client.token.encode('utf')).hexdigest(),
            md5(b','.join(s.encode('utf') for s in self.scopes)).hexdigest(),
            md5(owner.encode('utf-8')).hexdigest() if owner else '',
        )
        if no_cache:
            result = None
        else:
            result = redis.get(cache_key)

        if result is None:
            # TODO(dcramer): paginate
            if not owner:
                endpoint = '/user/repos'
                params = {'type': 'owner'}
            else:
                endpoint = '/orgs/{}/repos'.format(owner)
                params = {}
            result = []
            has_results = True
            while has_results and endpoint:
                response = self.client.get(endpoint, params=params)
                result.extend([{
                    'id': r['id'],
                    'ssh_url': r['ssh_url'],
                    'full_name': r['full_name'],
                    'admin': r['permissions'].get('admin', False),
                } for r in response])
                has_results = bool(response)
                if has_results:
                    endpoint = response.rel.get('next')
            redis.setex(
                cache_key, json.dumps(result), ONE_DAY
            )
        else:
            result = json.loads(result)
        return sorted(result, key=lambda x: x['full_name'])
