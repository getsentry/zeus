from zeus import factories
from zeus.models import RepositoryAccess, RepositoryBackend, RepositoryProvider


def test_repo_branch_list(client, db_session, default_login,
                          default_user, git_repo_config):
    repo = factories.RepositoryFactory.create(
        backend=RepositoryBackend.git,
        provider=RepositoryProvider.github,
        url=git_repo_config.url,
    )
    db_session.add(RepositoryAccess(user=default_user, repository=repo))
    db_session.flush()

    resp = client.get(
        '/api/repos/{}/branches'.format(
            repo.get_full_name())
    )

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0] == {'name': 'master'}
