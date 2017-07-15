from base64 import b64encode

from zeus import auth
from zeus.constants import Result
from zeus.models import Artifact, ItemStat, TestCase as ZeusTestCase
from zeus.utils.testresult import (
    TestResult as ZeusTestResult, TestResultManager as ZeusTestResultManager
)


def test_full(default_project, default_job):
    auth.set_current_tenant(
        auth.Tenant(
            organization_ids=[default_project.organization_id],
            project_ids=[default_project.id],
            repository_ids=[default_project.repository_id],
        )
    )

    results = [
        ZeusTestResult(
            job=default_job,
            name='test_bar',
            package='tests.changes.handlers.test_xunit',
            result=Result.failed,
            message='collection failed',
            duration=156,
            artifacts=[
                {
                    'name': 'artifact_name',
                    'type': 'text',
                    'base64': b64encode('sample content'.encode('utf-8'))
                }
            ]
        ),
        ZeusTestResult(
            job=default_job,
            name='test_foo',
            package='tests.changes.handlers.test_coverage',
            result=Result.passed,
            message='foobar failed',
            duration=12,
        ),
    ]
    manager = ZeusTestResultManager(default_job)
    manager.save(results)

    testcase_list = sorted(ZeusTestCase.query.all(), key=lambda x: x.name)

    assert len(testcase_list) == 2

    for test in testcase_list:
        assert test.job_id == default_job.id

    assert testcase_list[0].name == 'tests.changes.handlers.test_coverage.test_foo'
    assert testcase_list[0].result == Result.passed
    assert testcase_list[0].message == 'foobar failed'
    assert testcase_list[0].duration == 12

    assert testcase_list[1].name == 'tests.changes.handlers.test_xunit.test_bar'
    assert testcase_list[1].result == Result.failed
    assert testcase_list[1].message == 'collection failed'
    assert testcase_list[1].duration == 156

    artifacts = list(
        Artifact.query.unrestricted_unsafe().filter(Artifact.testcase_id == testcase_list[1].id)
    )
    assert len(artifacts) == 1
    assert artifacts[0].file.get_file().read() == b'sample content'

    teststat = ItemStat.query.filter(
        ItemStat.name == 'tests.count',
        ItemStat.item_id == default_job.id,
    )[0]
    assert teststat.value == 2

    teststat = ItemStat.query.filter(
        ItemStat.name == 'tests.failures',
        ItemStat.item_id == default_job.id,
    )[0]
    assert teststat.value == 1

    teststat = ItemStat.query.filter(
        ItemStat.name == 'tests.duration',
        ItemStat.item_id == default_job.id,
    )[0]
    assert teststat.value == 168
