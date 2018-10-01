from zeus.utils.upserts import upsert_change_request


def test_upsert_change_request_already_exists(
    client,
    db_session,
    default_login,
    default_repo,
    default_repo_access,
    default_repo_tenant,
    default_change_request,
):
    cr = upsert_change_request(
        default_change_request.repository_id,
        default_change_request.provider,
        default_change_request.external_id,
    )
    assert cr == default_change_request
