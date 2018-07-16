from zeus.tasks import delete_repo
from zeus.models import Repository, RepositoryAccess


def test_delete_repo_existing(mocker, default_repo, default_repo_access):
    delete_repo(default_repo.id)

    assert not Repository.query.unrestricted_unsafe().all()
    assert not RepositoryAccess.query.all()
