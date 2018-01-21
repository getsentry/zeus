from zeus import auth, factories
from zeus.models import Repository


def test_tenant_does_not_query_repo_without_access(default_repo):
    auth.set_current_tenant(auth.Tenant(repository_ids=[]))

    assert list(Repository.query.all()) == []


def test_tenant_queries_repo_with_tenant(default_repo):
    auth.set_current_tenant(auth.Tenant(repository_ids=[default_repo.id]))

    assert list(Repository.query.all()) == [default_repo]


def test_tenant_allows_public_repos(default_repo):
    auth.set_current_tenant(auth.Tenant(repository_ids=[]))
    repo = factories.RepositoryFactory(name='public', public=True)
    assert list(Repository.query.all()) == [repo]


def test_tenant_allows_public_repos_with_access(default_repo):
    auth.set_current_tenant(auth.Tenant(repository_ids=[default_repo.id]))
    repo = factories.RepositoryFactory(name='public', public=True)
    assert list(Repository.query.all()) == [default_repo, repo]
