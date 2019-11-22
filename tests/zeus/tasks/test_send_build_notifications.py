from zeus import factories
from zeus.tasks import send_build_notifications


def test_sends_failure(mocker, db_session, default_revision, default_tenant):
    mock_send_email_notification = mocker.patch(
        "zeus.notifications.email.send_email_notification"
    )

    build = factories.BuildFactory(revision=default_revision, failed=True)
    db_session.add(build)

    send_build_notifications(build.id)

    mock_send_email_notification.assert_called_once_with(build=build)


def test_does_not_send_passing(mocker, db_session, default_revision, default_tenant):
    mock_send_email_notification = mocker.patch(
        "zeus.notifications.email.send_email_notification"
    )

    build = factories.BuildFactory(revision=default_revision, passed=True)
    db_session.add(build)

    send_build_notifications(build.id)

    assert not mock_send_email_notification.mock_calls
