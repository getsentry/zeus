from zeus.constants import Permission
from zeus.models import RepositoryAccess
from zeus.tasks import sync_github_access


def test_grants_repo_access(
    client, mocker, db_session, responses, default_repo, default_user, default_identity
):
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

    sync_github_access(default_user.id)

    access = RepositoryAccess.query.filter(
        RepositoryAccess.repository_id == default_repo.id,
        RepositoryAccess.user_id == default_user.id,
    ).first()
    assert access
    assert access.permission == Permission.admin


def test_revokes_repo_access(
    client,
    mocker,
    db_session,
    responses,
    default_repo,
    default_repo_access,
    default_user,
    default_identity,
):
    responses.add(
        responses.GET,
        "https://api.github.com/user/orgs",
        json=[{"login": default_repo.owner_name, "permissions": {"admin": True}}],
    )

    responses.add(
        responses.GET,
        "https://api.github.com/orgs/{}/repos".format(default_repo.owner_name),
        json=[],
    )

    sync_github_access(default_user.id)

    access = RepositoryAccess.query.filter(
        RepositoryAccess.repository_id == default_repo.id,
        RepositoryAccess.user_id == default_user.id,
    ).first()
    assert not access


def test_updates_repo_access(
    client,
    mocker,
    db_session,
    responses,
    default_repo,
    default_repo_access,
    default_user,
    default_identity,
):
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
                "permissions": {"admin": False},
            }
        ],
    )

    sync_github_access(default_user.id)

    access = RepositoryAccess.query.filter(
        RepositoryAccess.repository_id == default_repo.id,
        RepositoryAccess.user_id == default_user.id,
    ).first()
    assert access
    assert access.permission == Permission.read
