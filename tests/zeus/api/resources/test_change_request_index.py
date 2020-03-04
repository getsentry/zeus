# from datetime import timedelta
from zeus import factories


def test_change_request_list(
    client, sqla_assertions, default_login, default_change_request, default_repo_access
):
    # Queries:
    # - Savepoint???
    # - Tenant
    # - Change Requests
    # - Builds
    # - Build Count (paginator)
    with sqla_assertions.assert_statement_count(5):
        resp = client.get("/api/change-requests")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["id"] == str(default_change_request.id)
        assert data[0]["latest_build"] is None


def test_change_request_list_with_latest_build(
    client,
    sqla_assertions,
    default_login,
    default_build,
    default_change_request,
    default_repo_access,
):
    # Queries:
    # - Savepoint???
    # - Tenant
    # - Change Requests
    # - fetch_builds_for_revisions
    #   - Builds
    #   - Build.authors
    #   - Revision.authors
    # - parent_revision.authors
    # - Item Stats
    # - Build Count (paginator)
    assert (
        default_build.repository_id
        == default_change_request.head_revision.repository_id
    )
    assert default_build.revision_sha == default_change_request.head_revision.sha
    with sqla_assertions.assert_statement_count(8):
        resp = client.get("/api/change-requests")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["id"] == str(default_change_request.id)
        assert data[0]["latest_build"]["status"] == "finished"


def test_change_request_list_without_access(
    client, sqla_assertions, default_login, default_change_request
):
    with sqla_assertions.assert_statement_count(1):
        resp = client.get("/api/change-requests")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 0


def test_change_request_list_excludes_public(
    client, sqla_assertions, default_repo_access, default_login
):
    repo = factories.RepositoryFactory.create(public=True)
    revision = factories.RevisionFactory.create(repository=repo)
    factories.ChangeRequestFactory.create(parent_revision=revision)
    with sqla_assertions.assert_statement_count(3):
        resp = client.get("/api/change-requests")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 0


# def test_change_request_list_user(
#     client,
#     sqla_assertions,
#     default_login,
#     default_repo,
#     default_repo_access,
#     default_revision,
#     default_source,
# ):
#     # unrelated build
#     factories.BuildFactory(repository=default_repo)

#     # "my" builds
#     cr2 = factories.BuildFactory(repository=default_repo, source=default_source)
#     cr1 = factories.BuildFactory(
#         repository=default_repo,
#         source=default_source,
#         date_created=build2.date_created - timedelta(minutes=1),
#     )

#     # Queries:
#     # - Tenant
#     # - Builds
#     # - Item Stats
#     # - Build Count (paginator)
#     with sqla_assertions.assert_statement_count(4):
#         resp = client.get("/api/change-requests?user=me")
#     assert resp.status_code == 200
#     data = resp.json()
#     # newly created build should not be present due to author email
#     assert len(data) == 2
#     assert data[0]["id"] == str(build2.id)
#     assert data[1]["id"] == str(build1.id)


# def test_change_request_list_repository(
#     client,
#     sqla_assertions,
#     default_login,
#     default_repo,
#     default_repo_access,
#     default_revision,
#     default_source,
# ):
#     # unrelated build
#     factories.BuildFactory()

#     # repo-specific builds
#     build2 = factories.BuildFactory(repository=default_repo, source=default_source)
#     build1 = factories.BuildFactory(
#         repository=default_repo,
#         source=default_source,
#         date_created=build2.date_created - timedelta(minutes=1),
#     )

#     # Queries:
#     # - Tenant
#     # - Repo
#     # - Builds
#     # - Item Stats
#     # - Build Count (paginator)
#     with sqla_assertions.assert_statement_count(5):
#         resp = client.get(
#             "/api/change-requests?repository={}".format(default_repo.get_full_name())
#         )
#     assert resp.status_code == 200
#     data = resp.json()
#     # newly created build should not be present due to author email
#     assert len(data) == 2
#     assert data[0]["id"] == str(build2.id)
#     assert data[1]["id"] == str(build1.id)
