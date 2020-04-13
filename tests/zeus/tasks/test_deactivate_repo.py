from zeus.constants import DeactivationReason
from zeus.models import ItemOption, RepositoryStatus
from zeus.tasks import deactivate_repo


def test_deactivate_repo(
    db_session, default_repo, default_repo_access, default_user, outbox
):
    db_session.add(
        ItemOption(item_id=default_repo.id, name="auth.private-key", value="")
    )
    db_session.flush()

    deactivate_repo(default_repo.id, DeactivationReason.invalid_pubkey)

    assert not ItemOption.query.filter(
        ItemOption.item_id == default_repo.id, ItemOption.name == "auth.private-key"
    ).first()
    assert default_repo.status == RepositoryStatus.inactive

    assert len(outbox) == 1
    msg = outbox[0]
    assert msg.subject == "Repository Disabled - getsentry/zeus"
    assert msg.recipients == [default_user.email]
