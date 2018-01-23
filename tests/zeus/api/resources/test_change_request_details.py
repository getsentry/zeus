from zeus.models import ChangeRequest


def test_change_request_details(client, db_session, default_login, default_repo,
                                default_change_request, default_repo_access):

    resp = client.get(
        '/api/repos/{}/change-requests/{}'.
        format(default_repo.get_full_name(), default_change_request.number)
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data['id'] == str(default_change_request.id)


def test_change_request_update(client, db_session, default_login, default_repo,
                               default_change_request, default_repo_access):

    resp = client.put(
        '/api/repos/{}/change-requests/{}'.
        format(default_repo.get_full_name(), default_change_request.number),
        json={
            'message': 'Hello world',
        }
    )
    assert resp.status_code == 200, resp.json()
    data = resp.json()
    assert data['id'] == str(default_change_request.id)

    cr = ChangeRequest.query.unrestricted_unsafe().get(default_change_request.id)
    assert cr.message == 'Hello world'
