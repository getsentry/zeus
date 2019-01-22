from datetime import timedelta

from zeus import factories
from zeus.models import RepositoryAccess, RepositoryBackend, RepositoryProvider
from zeus.utils import timezone


def test_revision_details(
    client, db_session, default_login, default_user, git_repo_config
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
    source = factories.SourceFactory.create(revision=revision)
    factories.BuildFactory.create(
        source=source, date_created=timezone.now() - timedelta(minutes=1)
    )
    factories.BuildFactory.create(source=source, passed=True)

    resp = client.get(
        "/api/repos/{}/revisions/{}".format(repo.get_full_name(), revision.sha)
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "finished"
