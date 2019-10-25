from zeus import auth, factories
from zeus.api.utils.upserts import upsert_change_request
from zeus.models import ChangeRequest, RepositoryProvider
from zeus.constants import Permission


def test_upsert_change_request_already_exists(
    client,
    db_session,
    default_login,
    default_repo,
    default_repo_write_tenant,
    default_change_request,
):
    cr = upsert_change_request(
        default_change_request.repository,
        default_change_request.provider,
        default_change_request.external_id,
    ).json()

    assert cr["id"] == str(default_change_request.id)
    assert ChangeRequest.query.count() == 1


def test_upsert_change_request_different_repos(
    client,
    db_session,
    default_repo,
    default_revision,
    default_change_request,
    default_user,
    mocker,
):
    """
    Check that two change requests from different repos can have the same external id
    """
    new_repo = factories.RepositoryFactory(public=True)

    auth.set_current_tenant(
        auth.Tenant(
            access={default_repo.id: Permission.write, new_repo.id: Permission.write}
        )
    )

    default_change_request.external_id = "id"
    default_change_request.provider = RepositoryProvider.github.value
    db_session.add(default_change_request)
    db_session.commit()

    mock_identify_revision = mocker.patch("zeus.utils.revisions.identify_revision")
    mock_identify_revision.return_value = factories.RevisionFactory(
        repository=new_repo, sha="1234567"
    )
    assert ChangeRequest.query.count() == 1

    cr = upsert_change_request(
        new_repo,
        default_change_request.provider,
        default_change_request.external_id,
        data={"message": "Hello", "parent_revision_sha": default_revision.sha},
    ).json()

    assert ChangeRequest.query.count() == 2
    new_change_request = ChangeRequest.query.filter(
        ChangeRequest.id != default_change_request.id
    ).first()
    assert cr["id"] == str(new_change_request.id)



def test_upsert_change_request_ref_only_existing_revision(
    client,
    db_session,
    default_repo,
    default_revision,
    default_change_request,
    default_user,
    mocker,
):
    auth.set_current_tenant(
        auth.Tenant(
            access={default_repo.id: Permission.write}
        )
    )

    mock_identify_revision = mocker.patch("zeus.utils.revisions.identify_revision")
    mock_identify_revision.return_value = factories.RevisionFactory(
        repository=default_repo, sha="1234567"
    )
    assert ChangeRequest.query.count() == 1

    data = upsert_change_request(
        default_repo,
        default_change_request.provider,
        default_change_request.external_id,
        data={"message": "Hello", "parent_ref": default_revision.sha[:8]},
    ).json()

    assert not mock_identify_revision.mock_calls

    assert ChangeRequest.query.count() == 1
    cr = ChangeRequest.query.get(data['id'])
    assert cr.parent_ref == default_revision.sha[:8]
    assert cr.parent_revision_sha == default_revision.sha


def test_upsert_change_request_ref_only_new_revision(
    client,
    db_session,
    default_repo,
    default_revision,
    default_change_request,
    default_user,
    mocker,
):
    auth.set_current_tenant(
        auth.Tenant(
            access={default_repo.id: Permission.write}
        )
    )

    mock_identify_revision = mocker.patch("zeus.utils.revisions.identify_revision")
    mock_identify_revision.return_value = factories.RevisionFactory(
        repository=default_repo, sha="1234567"
    )
    assert ChangeRequest.query.count() == 1

    data = upsert_change_request(
        default_repo,
        default_change_request.provider,
        default_change_request.external_id,
        data={"message": "Hello", "parent_ref": 'abcdefg'},
    ).json()

    assert not mock_identify_revision.mock_calls

    assert ChangeRequest.query.count() == 1
    cr = ChangeRequest.query.get(data['id'])
    assert cr.parent_ref == 'abcdefg'
    assert cr.parent_revision_sha is None
