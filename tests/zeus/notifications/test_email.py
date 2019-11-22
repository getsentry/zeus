from zeus import factories
from zeus.models import ItemOption
from zeus.notifications.email import send_email_notification


def test_success(
    mocker,
    db_session,
    default_user,
    default_repo,
    default_repo_access,
    default_revision,
    default_tenant,
    outbox,
):
    build = factories.BuildFactory(revision=default_revision, failed=True)
    db_session.add(build)

    send_email_notification(build)

    assert len(outbox) == 1
    msg = outbox[0]
    assert msg.subject == "Build Failed - getsentry/zeus #1"
    assert msg.recipients == [default_user.email]


def test_no_repo_access(
    mocker,
    db_session,
    default_tenant,
    default_user,
    default_repo,
    default_revision,
    outbox,
):
    build = factories.BuildFactory(revision=default_revision, failed=True)
    db_session.add(build)

    send_email_notification(build)

    assert len(outbox) == 0


def test_disabled(
    mocker,
    db_session,
    default_user,
    default_repo,
    default_repo_access,
    default_revision,
    default_tenant,
    outbox,
):
    build = factories.BuildFactory(revision=default_revision, failed=True)
    db_session.add(build)
    db_session.add(
        ItemOption(item_id=default_user.id, name="mail.notify_author", value="0")
    )
    db_session.flush()

    send_email_notification(build)

    assert len(outbox) == 0
