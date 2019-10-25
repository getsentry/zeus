from datetime import timedelta

from zeus import factories
from zeus.models import RepositoryAccess, RepositoryBackend, RepositoryProvider
from zeus.utils import timezone


def test_revision_artifacts(
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
    build = factories.BuildFactory.create(source=source, date_created=timezone.now())
    job = factories.JobFactory.create(build=build)
    artifact = factories.ArtifactFactory.create(job=job)

    resp = client.get(
        "/api/repos/{}/revisions/{}/artifacts".format(
            repo.get_full_name(), revision.sha
        )
    )

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == str(artifact.id)


def test_revision_artifacts_no_build(
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

    resp = client.get(
        "/api/repos/{}/revisions/{}/artifacts".format(
            repo.get_full_name(), revision.sha
        )
    )

    assert resp.status_code == 404
