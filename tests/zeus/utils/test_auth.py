from zeus import auth


def test_login_user(client, default_user):
    with client.session_transaction() as session:
        auth.login_user(default_user.id, session=session)
        assert session["uid"] == str(default_user.id)
        assert session["expire"]


def test_token_generation(default_user, default_repo, default_repo_access):
    tenant = auth.Tenant.from_user(default_user)
    token = auth.generate_token(tenant)
    assert isinstance(token, bytes)
    result = auth.parse_token(token)
    assert result["repo_ids"] == [str(default_repo.id)]
    assert result["uid"] == str(default_user.id)
