from uuid import UUID

from zeus.config import celery, db
from zeus.db.utils import create_or_update
from zeus.models import Repository, RepositoryAccess, RepositoryProvider, User
from zeus.vcs.providers.github import GitHubRepositoryProvider


def remove_access_to_owner_repos(user_id: UUID, owner_name: str, *filters):
    RepositoryAccess.query.filter(
        RepositoryAccess.user_id == user_id,
        RepositoryAccess.repository_id.in_(
            db.session.query(RepositoryAccess.repository_id).join(
                Repository, Repository.id == RepositoryAccess.repository_id,
            ).filter(
                Repository.provider == RepositoryProvider.github,
                Repository.owner_name == owner_name,
                RepositoryAccess.user_id == user_id,
                *filters
            ).subquery()
        ),
    ).delete(synchronize_session=False)


def sync_repos_for_owner(provider: GitHubRepositoryProvider, user: User, owner_name: str):
    repo_permissions = {
        r['name']: r['permission']
        for r in provider.get_repos_for_owner(user, owner_name)
    }

    if not repo_permissions:
        remove_access_to_owner_repos(user.id, owner_name)
        return

    # first clear any access to repos which are no longer part of the organization
    remove_access_to_owner_repos(
        user.id, owner_name, ~Repository.name.in_(repo_permissions.keys()))

    # now identify any repos which might need access granted or updated
    matches = list(Repository.query.unrestricted_unsafe().filter(
        Repository.provider == RepositoryProvider.github,
        Repository.owner_name == owner_name,
        Repository.name.in_(repo_permissions.keys())
    ))

    for repo in matches:
        permission = repo_permissions.get(repo.name)
        if permission:
            create_or_update(RepositoryAccess, where={
                'repository_id': repo.id,
                'user_id': user.id,
            }, values={
                'permission': permission,
            })
        else:
            # revoke permissions -- this path shouldnt really get hit
            RepositoryAccess.query.filter(
                RepositoryAccess.repository_id == repo.id,
                RepositoryAccess.user_id == user.id,
            ).delete()


@celery.task(max_retries=None, autoretry_for=(Exception,), acks_late=True)
def sync_github_access(user_id: UUID):
    user = User.query.get(user_id)
    if not user:
        return

    provider = GitHubRepositoryProvider(cache=True)
    owner_list = [o['name'] for o in provider.get_owners(user)]
    # for each owner list, we need to see if there are any matching repos
    if owner_list:
        for owner_name in owner_list:
            sync_repos_for_owner(provider, user, owner_name)

    db.session.commit()
