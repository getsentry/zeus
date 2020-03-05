from datetime import timedelta
from zeus import factories


def test_build_list(
    client, sqla_assertions, default_login, default_build, default_repo_access
):
    # Queries:
    # - Savepoint???
    # - Tenant
    # - Builds
    # - Build.authors
    # - Revision.authors
    # - Item Stats
    # - Build Count (paginator)
    with sqla_assertions.assert_statement_count(7):
        resp = client.get("/api/builds")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["id"] == str(default_build.id)


def test_build_list_without_access(
    client, sqla_assertions, default_login, default_build
):
    with sqla_assertions.assert_statement_count(1):
        resp = client.get("/api/builds")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 0


def test_build_list_excludes_public(
    client, sqla_assertions, default_repo_access, default_login
):
    repo = factories.RepositoryFactory(public=True)
    factories.BuildFactory(repository=repo)
    with sqla_assertions.assert_statement_count(3):
        resp = client.get("/api/builds")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 0


def test_build_list_user(
    client,
    sqla_assertions,
    default_author,
    default_login,
    default_repo,
    default_repo_access,
    default_revision,
):
    # unrelated build
    factories.BuildFactory(repository=default_repo)

    # "my" builds
    build2 = factories.BuildFactory(
        repository=default_repo, revision=default_revision, authors=[default_author]
    )
    build1 = factories.BuildFactory(
        repository=default_repo,
        revision=default_revision,
        date_created=build2.date_created - timedelta(minutes=1),
        authors=[default_author],
    )

    # Queries:
    # - Tenant
    # - Builds
    # - Build.authors
    # - Revision.authors
    # - Item Stats
    # - Build Count (paginator)
    with sqla_assertions.assert_statement_count(6):
        resp = client.get("/api/builds?user=me")
        assert resp.status_code == 200
        data = resp.json()
        # newly created build should not be present due to author email
        assert len(data) == 2
        assert data[0]["id"] == str(build2.id)
        assert data[1]["id"] == str(build1.id)


def test_build_list_repository(
    client,
    sqla_assertions,
    default_login,
    default_repo,
    default_repo_access,
    default_revision,
):
    # unrelated build
    factories.BuildFactory()

    # repo-specific builds
    build2 = factories.BuildFactory(repository=default_repo, revision=default_revision)
    build1 = factories.BuildFactory(
        repository=default_repo,
        revision=default_revision,
        date_created=build2.date_created - timedelta(minutes=1),
    )

    # Queries:
    # - Tenant
    # - Repo
    # - Builds
    # - Build.authors
    # - Revision.authors
    # - Item Stats
    # - Build Count (paginator)
    with sqla_assertions.assert_statement_count(7):
        resp = client.get(
            "/api/builds?repository={}".format(default_repo.get_full_name())
        )
        assert resp.status_code == 200
        data = resp.json()
        # newly created build should not be present due to author email
        assert len(data) == 2
        assert data[0]["id"] == str(build2.id)
        assert data[1]["id"] == str(build1.id)
