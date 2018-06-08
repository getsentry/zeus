from urllib.parse import parse_qs

from zeus import factories
from zeus.constants import GITHUB_AUTH_URI, GITHUB_TOKEN_URI, Permission
from zeus.models import Email, Identity, RepositoryAccess, User


def test_login(client):
    resp = client.get("/auth/github")
    assert resp.status_code == 302
    location, querystring = resp.headers["Location"].split("?", 1)
    assert location == GITHUB_AUTH_URI
    qs = parse_qs(querystring)
    assert qs["client_id"] == ["github.client-id"]
    assert qs["redirect_uri"] == ["http://localhost/auth/github/complete"]
    assert qs["response_type"] == ["code"]
    assert sorted(qs["scope"][0].split(",")) == ["read:org", "repo", "user:email"]


def test_login_complete(client, db_session, mocker, responses):
    responses.add(
        "POST",
        GITHUB_TOKEN_URI,
        json={
            "token_type": "bearer",
            "scope": "user:email,read:org",
            "access_token": "access-token",
        },
    )

    # TOOD(dcramer): ideally we could test the header easily, but responses
    # doesnt make that highly accessible yet
    responses.add(
        "GET",
        "https://api.github.com/user",
        match_querystring=True,
        json={"id": 1, "login": "test", "email": "foo@example.com"},
    )
    responses.add(responses.GET, "https://api.github.com/user/orgs", json=[])
    responses.add(
        "GET",
        "https://api.github.com/user/emails",
        match_querystring=True,
        json=[
            {"email": "foo@example.com", "verified": True, "primary": True},
            {"email": "foo.bar@example.com", "verified": False, "primary": False},
        ],
    )

    resp = client.get("/auth/github/complete?code=abc")

    assert resp.status_code == 302, repr(resp)
    assert resp.headers["Location"] == "http://localhost/"

    user = User.query.filter(User.email == "foo@example.com").first()

    assert user

    identity = Identity.query.filter(Identity.user_id == user.id).first()

    assert identity
    assert identity.provider == "github"
    assert identity.external_id == "1"
    assert identity.scopes == ["user:email", "read:org"]
    assert identity.config == {
        "access_token": "access-token",
        "refresh_token": None,
        "login": "test",
    }

    emails = {
        r[0]: r[1]
        for r in db_session.query(Email.email, Email.verified).filter(
            Email.user_id == user.id
        )
    }
    assert emails.get("foo@example.com") is True
    assert emails.get("foo.bar@example.com") is False
    assert emails.get("test@users.noreply.github.com") is True


def test_login_complete_no_visible_email(client, mocker, responses):
    responses.add(
        "POST",
        GITHUB_TOKEN_URI,
        json={
            "token_type": "bearer",
            "scope": "user:email,read:org",
            "access_token": "access-token",
        },
    )
    responses.add(responses.GET, "https://api.github.com/user/orgs", json=[])

    # TOOD(dcramer): ideally we could test the header easily, but responses
    # doesnt make that highly accessible yet
    responses.add(
        "GET",
        "https://api.github.com/user",
        match_querystring=True,
        body='{"id": 1, "login": "test", "email": null}',
    )
    responses.add(
        "GET",
        "https://api.github.com/user/emails",
        match_querystring=True,
        json=[{"email": "foo@example.com", "verified": True, "primary": True}],
    )

    resp = client.get("/auth/github/complete?code=abc")

    assert resp.status_code == 302
    assert resp.headers["Location"] == "http://localhost/"

    user = User.query.filter(User.email == "foo@example.com").first()

    assert user


def test_login_complete_automatic_repo_access(
    client, mocker, db_session, responses, default_repo
):
    responses.add(
        "POST",
        GITHUB_TOKEN_URI,
        json={
            "token_type": "bearer",
            "scope": "user:email,read:org",
            "access_token": "access-token",
        },
    )

    # TOOD(dcramer): ideally we could test the header easily, but responses
    # doesnt make that highly accessible yet
    responses.add(
        responses.GET,
        "https://api.github.com/user",
        match_querystring=True,
        json={"id": 1, "login": "test", "email": "foo@example.com"},
    )
    responses.add(
        "GET",
        "https://api.github.com/user/emails",
        match_querystring=True,
        json=[{"email": "foo@example.com", "verified": True, "primary": True}],
    )
    responses.add(
        responses.GET,
        "https://api.github.com/user/orgs",
        json=[{"login": default_repo.owner_name, "permissions": {"admin": True}}],
    )

    responses.add(
        responses.GET,
        "https://api.github.com/orgs/{}/repos".format(default_repo.owner_name),
        json=[
            {
                "id": default_repo.external_id,
                "name": default_repo.name,
                "full_name": default_repo.data["full_name"],
                "clone_url": "https://github.com/{}.git".format(
                    default_repo.data["full_name"]
                ),
                "ssh_url": "git@github.com:getsentry/zeus.git",
                "permissions": {"admin": True},
            }
        ],
    )

    resp = client.get("/auth/github/complete?code=abc")

    assert resp.status_code == 302
    assert resp.headers["Location"] == "http://localhost/"

    user = User.query.filter(User.email == "foo@example.com").first()

    assert user

    identity = Identity.query.filter(Identity.user_id == user.id).first()

    assert identity
    assert identity.provider == "github"
    assert identity.external_id == "1"
    assert identity.config == {
        "access_token": "access-token",
        "refresh_token": None,
        "login": "test",
    }
    assert identity.scopes == ["user:email", "read:org"]

    access = RepositoryAccess.query.filter(
        RepositoryAccess.repository_id == default_repo.id,
        RepositoryAccess.user_id == user.id,
    ).first()
    assert access
    assert access.permission == Permission.admin


def test_login_complete_existing_user_no_identity(
    client, db_session, mocker, responses
):
    responses.add(
        "POST",
        GITHUB_TOKEN_URI,
        json={
            "token_type": "bearer",
            "scope": "user:email,read:org",
            "access_token": "access-token",
        },
    )

    # TOOD(dcramer): ideally we could test the header easily, but responses
    # doesnt make that highly accessible yet
    responses.add(
        "GET",
        "https://api.github.com/user",
        match_querystring=True,
        json={"id": 1, "login": "test", "email": "foo@example.com"},
    )
    # responses.add(responses.GET, 'https://api.github.com/user/orgs', json=[])
    responses.add(
        "GET",
        "https://api.github.com/user/emails",
        match_querystring=True,
        json=[
            {"email": "foo@example.com", "verified": True, "primary": True},
            {"email": "foo.bar@example.com", "verified": False, "primary": False},
        ],
    )

    user = factories.UserFactory.create(email="foo@example.com")

    resp = client.get("/auth/github/complete?code=abc")

    assert resp.status_code == 302
    assert resp.headers["Location"] == "http://localhost/"

    identity = Identity.query.filter(Identity.user_id == user.id).first()

    assert identity
    assert identity.provider == "github"
    assert identity.external_id == "1"
    assert identity.config == {
        "access_token": "access-token",
        "refresh_token": None,
        "login": "test",
    }
    assert identity.scopes == ["user:email", "read:org"]

    emails = {
        r[0]: r[1]
        for r in db_session.query(Email.email, Email.verified).filter(
            Email.user_id == user.id
        )
    }
    assert emails.get("foo@example.com") is True
    assert emails.get("foo.bar@example.com") is False
    assert emails.get("test@users.noreply.github.com") is True


def test_login_complete_existing_identity(client, db_session, mocker, responses):
    responses.add(
        "POST",
        GITHUB_TOKEN_URI,
        json={
            "token_type": "bearer",
            "scope": "user:email,read:org",
            "access_token": "access-token",
        },
    )

    # TOOD(dcramer): ideally we could test the header easily, but responses
    # doesnt make that highly accessible yet
    responses.add(
        "GET",
        "https://api.github.com/user",
        match_querystring=True,
        json={"id": 1, "login": "test", "email": "foo@example.com"},
    )
    # responses.add(responses.GET, 'https://api.github.com/user/orgs', json=[])
    responses.add(
        "GET",
        "https://api.github.com/user/emails",
        match_querystring=True,
        json=[
            {"email": "foo@example.com", "verified": True, "primary": True},
            {"email": "foo.bar@example.com", "verified": False, "primary": False},
        ],
    )

    user = factories.UserFactory.create(email="foo@example.com")
    identity = factories.IdentityFactory.create(
        user=user, provider="github", external_id="1"
    )

    resp = client.get("/auth/github/complete?code=abc")

    assert resp.status_code == 302
    assert resp.headers["Location"] == "http://localhost/"

    identity = Identity.query.filter(Identity.user_id == user.id).first()

    assert identity
    assert identity.provider == "github"
    assert identity.external_id == "1"
    assert identity.config == {
        "access_token": "access-token",
        "refresh_token": None,
        "login": "test",
    }
    assert identity.scopes == ["user:email", "read:org"]

    emails = {
        r[0]: r[1]
        for r in db_session.query(Email.email, Email.verified).filter(
            Email.user_id == user.id
        )
    }
    assert emails.get("foo@example.com") is True
    assert emails.get("foo.bar@example.com") is False
    assert emails.get("test@users.noreply.github.com") is True
