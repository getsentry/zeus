from datetime import timedelta

from zeus import factories
from zeus.models import RepositoryAccess, RepositoryBackend, RepositoryProvider
from zeus.utils import timezone


def test_repo_revision_list(
    client, db_session, default_login, default_user, git_repo_config, mock_vcs_server
):
    repo = factories.RepositoryFactory.create(
        backend=RepositoryBackend.git,
        provider=RepositoryProvider.github,
        url=git_repo_config.url,
    )
    db_session.add(RepositoryAccess(user=default_user, repository=repo))
    db_session.flush()

    revision = factories.RevisionFactory.create(
        sha=git_repo_config.commits[0], repository=repo
    )
    factories.BuildFactory.create(
        revision=revision, date_created=timezone.now() - timedelta(minutes=1)
    )
    factories.BuildFactory.create(revision=revision, passed=True)

    resp = client.get("/api/repos/{}/revisions".format(repo.get_full_name()))

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["sha"] == git_repo_config.commits[0]
    assert data[0]["latest_build"]["status"] == "finished"
    assert data[1]["sha"] == git_repo_config.commits[1]
    assert data[1]["latest_build"] is None
