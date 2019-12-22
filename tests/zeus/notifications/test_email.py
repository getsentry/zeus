from zeus import factories
from zeus.models import ItemOption, RepositoryAccess
from zeus.notifications.email import find_linked_emails, send_email_notification


def test_success(
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
    db_session, default_tenant, default_user, default_repo, default_revision, outbox
):
    build = factories.BuildFactory(revision=default_revision, failed=True)
    db_session.add(build)

    send_email_notification(build)

    assert len(outbox) == 0


def test_disabled(
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


def test_find_linked_emails(
    db_session,
    default_user,
    default_repo,
    default_repo_access,
    default_revision,
    default_tenant,
    outbox,
):
    other_user = factories.UserFactory()
    factories.AuthorFactory(repository=default_repo, email=other_user.email)
    factories.EmailFactory(user=other_user, email=other_user.email)
    access = RepositoryAccess(user_id=other_user.id, repository_id=default_repo.id)
    db_session.add(access)

    build = factories.BuildFactory(revision=default_revision)
    db_session.add(build)

    results = find_linked_emails(build)
    assert results == [(default_user.id, default_user.email)]
