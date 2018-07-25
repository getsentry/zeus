
from datetime import timedelta

from zeus import factories


def test_user_build_list(
    client,
    sqla_assertions,
    default_login,
    default_repo,
    default_repo_access,
    default_revision,
    default_source,
):
    # unrelated build
    factories.BuildFactory(repository=default_repo)

    # "my" builds
    build2 = factories.BuildFactory(repository=default_repo, source=default_source)
    build1 = factories.BuildFactory(
        repository=default_repo,
        source=default_source,
        date_created=build2.date_created - timedelta(minutes=1),
    )

    # Queries:
    # - Tenant
    # - Builds
    # - Item Stats
    # - Build Count (paginator)
    with sqla_assertions.assert_statement_count(4):
        resp = client.get("/api/users/me/builds".format(default_repo.name))
    assert resp.status_code == 200
    data = resp.json()
    # newly created build should not be present due to author email
    assert len(data) == 2
    assert data[0]["id"] == str(build2.id)
    assert data[1]["id"] == str(build1.id)
