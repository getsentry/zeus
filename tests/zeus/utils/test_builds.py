from datetime import datetime, timedelta

from zeus import factories
from zeus.constants import Status, Result
from zeus.utils.builds import fetch_build_for_revision, merge_build_group


def test_merge_build_group_different_providers(client, default_login, default_source):
    now = datetime.now()
    later = now + timedelta(minutes=1)
    build1 = factories.BuildFactory.create(
        source=default_source, provider="provider1", date_started=now, date_finished=now
    )
    build2 = factories.BuildFactory.create(
        source=default_source,
        provider="provider2",
        date_started=later,
        date_finished=later,
    )

    merged_build = merge_build_group([build1, build2])

    assert merged_build.source == default_source
    assert merged_build.label == default_source.revision.message
    assert merged_build.original == [build1, build2]
    assert merged_build.status == Status(max(build1.status.value, build2.status.value))
    assert merged_build.result == Result(max(build1.result.value, build2.result.value))
    assert merged_build.date_started == now
    assert merged_build.date_finished == later
    assert merged_build.provider == "provider1, provider2"


def test_merge_build_group_empty_dates(client, default_login, default_source):
    now = datetime.now()
    build1 = factories.BuildFactory.create(
        source=default_source, provider="provider1", date_started=now, date_finished=now
    )
    build2 = factories.BuildFactory.create(
        source=default_source,
        provider="provider2",
        date_started=None,
        date_finished=None,
    )

    merged_build = merge_build_group([build1, build2])

    assert merged_build.date_started == now
    assert merged_build.date_finished == now


def test_fetch_build_with_required_hooks(
    client, db_session, default_login, default_tenant, default_repo, default_source
):
    hook1 = factories.HookFactory.create(repository_id=default_repo.id)
    hook2 = factories.HookFactory.create(repository_id=default_repo.id)
    default_source.data = {"required_hook_ids": [str(hook1.id), str(hook2.id)]}
    db_session.add(default_source)
    db_session.commit()

    factories.BuildFactory.create(source=default_source, hook_id=hook1.id, passed=True)

    merged_build = fetch_build_for_revision(default_source.revision)

    assert merged_build.result == Result.failed

    factories.BuildFactory.create(source=default_source, hook_id=hook2.id, passed=True)

    merged_build = fetch_build_for_revision(default_source.revision)

    assert merged_build.result == Result.passed
