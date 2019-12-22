from zeus.tasks import delete_repo
from zeus.models import Repository, RepositoryAccess, RepositoryStatus


def test_delete_repo_existing_marked_inactive(
    db_session, default_repo, default_repo_access
):
    default_repo.status = RepositoryStatus.inactive
    db_session.add(default_repo)
    db_session.flush()

    delete_repo(default_repo.id)

    assert not Repository.query.unrestricted_unsafe().all()
    assert not RepositoryAccess.query.all()


def test_delete_repo_existing_marked_active(default_repo, default_repo_access):
    assert default_repo.status == RepositoryStatus.active

    delete_repo(default_repo.id)

    assert Repository.query.unrestricted_unsafe().get(default_repo.id)
