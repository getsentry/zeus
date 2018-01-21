from zeus import auth, factories
from zeus.models import Build


def test_tenant_limits_to_access(default_repo):
    auth.set_current_tenant(auth.Tenant(repository_ids=[default_repo.id]))
    build = factories.BuildFactory(repository=default_repo)
    assert list(Build.query.all()) == [build]


def test_tenant_allows_public_repos(default_repo):
    auth.set_current_tenant(auth.Tenant(repository_ids=[default_repo.id]))
    repo = factories.RepositoryFactory(name='public', public=True)
    build = factories.BuildFactory(repository=repo)
    assert list(Build.query.all()) == [build]


def test_tenant_allows_public_repos_with_acess(default_repo):
    auth.set_current_tenant(auth.Tenant(repository_ids=[]))
    repo = factories.RepositoryFactory(name='public', public=True)
    build = factories.BuildFactory(repository=repo)
    assert list(Build.query.all()) == [build]
