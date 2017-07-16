import responses

ORG_LIST_RESPONSE = """[{
    "id": 1,
    "login": "getsentry"
}]"""


def test_list_github_organizations(client, default_login, default_user, default_identity):
    responses.add(
        'GET', 'https://api.github.com/user/orgs', match_querystring=True, body=ORG_LIST_RESPONSE
    )

    resp = client.get('/api/github/orgs')
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]['name'] == 'getsentry'
