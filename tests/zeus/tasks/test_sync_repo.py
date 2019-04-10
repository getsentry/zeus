from datetime import datetime

from zeus.tasks import sync_repo
from zeus.models import ItemOption, Repository, RepositoryStatus
from zeus.vcs.base import InvalidPublicKey, Vcs, RevisionResult


def test_sync_repo(mocker, db_session, default_repo):
    mock_vcs_backend = mocker.MagicMock(spec=Vcs)
    mock_get_vcs = mocker.patch.object(
        Repository, "get_vcs", return_value=mock_vcs_backend
    )

    def log(parent):
        if parent is None:
            yield RevisionResult(
                sha="a" * 40,
                message="hello world!",
                author="Example <foo@example.com>",
                author_date=datetime(2013, 9, 19, 22, 15, 22),
            )

    mock_vcs_backend.log.side_effect = log

    sync_repo(repo_id=default_repo.id)

    mock_get_vcs.assert_called_once_with()
    mock_vcs_backend.log.assert_any_call(parent=None)
    mock_vcs_backend.log.assert_any_call(parent="a" * 40)

    assert default_repo.last_update_attempt is not None
    assert default_repo.last_update is not None
    assert default_repo.status == RepositoryStatus.active

    # build sync is abstracted via sync_with_builder
    mock_vcs_backend.update.assert_called_once_with(allow_cleanup=True)


def test_invalid_public_key(mocker, db_session, default_repo):
    option = ItemOption(item_id=default_repo.id, name="auth.private-key", value="foo")
    db_session.add(option)
    db_session.flush()

    mock_vcs_backend = mocker.MagicMock(spec=Vcs)
    mocker.patch.object(Repository, "get_vcs", return_value=mock_vcs_backend)

    mock_vcs_backend.exists.return_value = False
    mock_vcs_backend.clone.side_effect = InvalidPublicKey(["git", "clone"], 1)

    sync_repo(repo_id=default_repo.id)

    assert default_repo.status == RepositoryStatus.inactive
    assert not ItemOption.query.get(option.id)
