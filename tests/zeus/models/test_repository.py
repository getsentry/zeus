from zeus import auth, factories
from zeus.constants import Permission
from zeus.models import Repository


def test_tenant_does_not_query_repo_without_access(default_repo):
    auth.set_current_tenant(auth.Tenant())
    assert list(Repository.query.all()) == []


def test_tenant_queries_repo_with_tenant(default_repo):
    auth.set_current_tenant(auth.Tenant(
        access={default_repo.id: Permission.read}))

    assert list(Repository.query.all()) == [default_repo]


def test_tenant_allows_public_repos(default_repo):
    auth.set_current_tenant(auth.Tenant())
    repo = factories.RepositoryFactory(name='public', public=True)
    assert list(Repository.query.all()) == [repo]


def test_tenant_allows_public_repos_with_access(default_repo):
    auth.set_current_tenant(auth.Tenant(
        access={default_repo.id: Permission.read}))
    repo = factories.RepositoryFactory(name='public', public=True)
    assert list(Repository.query.all()) == [default_repo, repo]
