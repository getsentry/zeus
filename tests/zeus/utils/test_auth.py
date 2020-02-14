from zeus import auth
from zeus.constants import Permission


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
    assert result["access"] == {str(default_repo.id): Permission.admin}
    assert result["uid"] == str(default_user.id)


def test_redirect_target(client, default_user):
    with client.session_transaction() as session:
        auth.bind_redirect_target("/gh/getsentry/zeus", session=session)
        assert (
            auth.get_redirect_target(clear=False, session=session)
            == "/gh/getsentry/zeus"
        )
        assert (
            auth.get_redirect_target(clear=True, session=session)
            == "/gh/getsentry/zeus"
        )
        assert auth.get_redirect_target(session=session) is None


def test_get_tenant_from_signed_token_user(
    default_user, default_repo, default_repo_access
):
    # TODO(dcramer): we'd prefer to not generate a dynamic token
    tenant = auth.Tenant.from_user(default_user)
    token = auth.generate_token(tenant)
    tenant = auth.get_tenant_from_signed_token(token)
    assert tenant.user_id == default_user.id
    assert tenant.access == {default_repo.id: Permission.admin}


def test_get_tenant_from_headers_token(default_user, default_repo, default_repo_access):
    # TODO(dcramer): we'd prefer to not generate a dynamic token
    tenant = auth.Tenant.from_user(default_user)
    token = auth.generate_token(tenant).decode("utf-8")
    tenant = auth.get_tenant_from_headers({"Authorization": f"Bearer zeus-t-{token}"})
    assert tenant.user_id == default_user.id
    assert tenant.access == {default_repo.id: Permission.admin}
