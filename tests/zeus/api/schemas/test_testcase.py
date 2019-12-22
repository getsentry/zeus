from dataclasses import dataclass
from datetime import timedelta
from typing import List, Tuple

from zeus import auth, factories
from zeus.constants import Permission, Result
from zeus.api.schemas import AggregateTestCaseSummarySchema


@dataclass
class AggregateTestCase:
    hash: str
    name: str
    # [id, job_id, duration, result]
    runs: List[Tuple[str, str, int, Result]]


def test_failure_origin(default_repo):
    auth.set_current_tenant(auth.Tenant(access={default_repo.id: Permission.read}))

    new_revision = factories.RevisionFactory(repository=default_repo)
    new_build = factories.BuildFactory(revision=new_revision, failed=True)
    new_job = factories.JobFactory(build=new_build, failed=True)
    new_testcase = factories.TestCaseFactory(job=new_job, failed=True)
    new_testcase2 = factories.TestCaseFactory(job=new_job, passed=True)

    old_revision = factories.RevisionFactory(
        repository=default_repo,
        date_created=new_revision.date_created - timedelta(hours=1),
    )
    old_build = factories.BuildFactory(
        revision=old_revision,
        failed=True,
        date_created=new_build.date_created - timedelta(hours=1),
    )
    old_job = factories.JobFactory(
        build=old_build,
        failed=True,
        date_created=new_job.date_created - timedelta(hours=1),
    )
    factories.TestCaseFactory(job=old_job, failed=True, name=new_testcase.name)

    oldold_revision = factories.RevisionFactory(
        repository=default_repo,
        date_created=old_revision.date_created - timedelta(hours=1),
    )
    factories.BuildFactory(
        revision=oldold_revision,
        passed=True,
        date_created=old_build.date_created - timedelta(hours=1),
    )

    schema = AggregateTestCaseSummarySchema(many=True, context={"build": new_build})
    result = schema.dump(
        [
            AggregateTestCase(
                hash=new_testcase.hash,
                name=new_testcase.name,
                runs=[
                    [
                        str(new_testcase.id),
                        str(new_testcase.job_id),
                        new_testcase.duration,
                        int(new_testcase.result),
                    ]
                ],
            ),
            AggregateTestCase(
                hash=new_testcase2.hash,
                name=new_testcase2.name,
                runs=[
                    [
                        str(new_testcase2.id),
                        str(new_testcase2.job_id),
                        new_testcase2.duration,
                        int(new_testcase2.result),
                    ]
                ],
            ),
        ]
    )
    assert len(result) == 2
    assert result[0]["hash"] == new_testcase.hash
    assert result[0]["name"] == new_testcase.name
    assert result[0]["origin_build"]["id"] == str(old_build.id)
    assert result[1]["hash"] == new_testcase2.hash
    assert result[1]["name"] == new_testcase2.name
    assert result[1]["origin_build"] is None
