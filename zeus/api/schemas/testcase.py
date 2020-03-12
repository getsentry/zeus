__all__ = ("AggregateTestCaseSummarySchema", "TestCaseSummarySchema", "TestCaseSchema")

from collections import defaultdict
from marshmallow import Schema, fields, pre_dump
from sqlalchemy import and_
from typing import Dict, List, Optional
from uuid import UUID

from zeus.config import db
from zeus.constants import Result, Status
from zeus.exceptions import UnknownRevision
from zeus.models import Build, Job, Revision, TestCase
from zeus.utils.aggregation import aggregate_result
from zeus.vcs import vcs_client

from .build import BuildSchema
from .fields import ResultField
from .job import JobSchema


def find_failure_origins(
    build: Build, test_failures: List[str]
) -> Dict[str, Optional[UUID]]:
    """
    Attempt to find originating causes of failures.

    Returns a mapping of {TestCase.hash: Job}.
    """
    if not test_failures:
        return {}

    repo = build.repository
    try:
        valid_revisions = [
            c["sha"]
            for c in vcs_client.log(repo.id, limit=100, parent=build.revision_sha)
        ]
    except UnknownRevision:
        valid_revisions = []

    filters = [
        Build.repository_id == build.repository_id,
        Build.status == Status.finished,
        Build.revision_sha != build.revision_sha,
    ]
    if valid_revisions:
        filters.extend([Build.revision_sha.in_(valid_revisions)])

    # NOTE(dcramer): many of these queries ignore tenant constraints
    # find any existing failures in the previous runs
    # to do this we first need to find the last passing build
    last_pass = (
        db.session.query(Revision.sha, Revision.date_created)
        .join(
            Build,
            and_(
                Revision.sha == Build.revision_sha,
                Revision.repository_id == Build.repository_id,
            ),
        )
        .filter(
            Build.result == Result.passed,
            Revision.date_created <= build.revision.date_created,
            Build.date_created <= build.date_created,
            *filters,
        )
        .order_by(Revision.date_created.desc())
        .first()
    )

    if last_pass:
        last_pass_revision_sha, last_pass_date = last_pass

        # We have to query all runs between build and last_pass. Because we're
        # paranoid about performance, we limit this to 100 results.
        previous_build_ids = [
            r
            for r, in db.session.query(Build.id)
            .join(
                Revision,
                and_(
                    Revision.sha == Build.revision_sha,
                    Revision.repository_id == Build.repository_id,
                ),
            )
            .filter(
                Build.result == Result.failed,
                Build.date_created >= last_pass_date,
                Revision.date_created >= last_pass_date,
                Revision.sha != last_pass_revision_sha,
                *filters,
            )
            .order_by(Revision.date_created.desc())[:100]
        ]
    else:
        previous_build_ids = [
            r
            for r, in db.session.query(Build.id)
            .join(
                Revision,
                and_(
                    Revision.sha == Build.revision_sha,
                    Revision.repository_id == Build.repository_id,
                ),
            )
            .filter(Build.result == Result.failed, *filters)
            .order_by(Revision.date_created.desc())[:100]
        ]

    if not previous_build_ids:
        return {}

    # we now have a list of previous_runs so let's find all test failures in
    # these runs
    queryset = (
        db.session.query(TestCase.hash, Job.build_id)
        .join(Job, Job.id == TestCase.job_id)
        .filter(
            Job.build_id.in_(previous_build_ids),
            Job.status == Status.finished,
            Job.result == Result.failed,
            TestCase.result == Result.failed,
            TestCase.hash.in_(test_failures),
        )
        .group_by(TestCase.hash, Job.build_id)
    )

    previous_test_failures = defaultdict(set)
    for test_hash, build_id in queryset:
        previous_test_failures[build_id].add(test_hash)

    failures_at_build: Dict[str, Optional[UUID]] = {}
    searching = set(t for t in test_failures)
    # last_checked_run = build.id
    last_checked_run = None

    for p_build in previous_build_ids:
        p_build_failures = previous_test_failures[p_build]
        # we have to copy the set as it might change size during iteration
        for f_test in list(searching):
            if f_test not in p_build_failures:
                failures_at_build[f_test] = last_checked_run
                searching.remove(f_test)
        last_checked_run = p_build

    for f_test in searching:
        failures_at_build[f_test] = last_checked_run

    return failures_at_build


class ExecutionSchema(Schema):
    id = fields.UUID(dump_only=True)
    result = ResultField(required=True)
    duration = fields.Number()
    job_id = fields.UUID(required=True)


class AggregateTestCaseSummarySchema(Schema):
    name = fields.Str(required=True)
    hash = fields.Str(dump_only=True)
    runs = fields.List(fields.Nested(ExecutionSchema), required=True)
    result = ResultField(required=True)
    message = fields.Str(required=False)
    build = fields.Nested(
        BuildSchema(exclude=("repository", "revision", "stats")), required=False
    )
    origin_build = fields.Nested(
        BuildSchema(exclude=("repository", "revision", "stats")), required=False
    )

    @pre_dump(pass_many=True)
    def process_aggregates(self, data, many, **kwargs):
        if not many:
            items = [data]
        else:
            items = data
        if "origin_build" in self.exclude or "build" not in self.context:
            failure_origins = {}
        else:
            # TODO(dcramer): technically this could support multiple builds,
            # or identify the referenced build
            failure_origins = find_failure_origins(
                self.context["build"],
                [
                    i.hash
                    for i in items
                    if any(Result(int(e[3])) == Result.failed for e in i.runs)
                ],
            )

        if "build" in self.exclude or not hasattr(items[0], "build_id"):
            builds = {}
        else:
            builds = {
                b.id: b
                for b in Build.query.filter(Build.id.in_(i.build_id for i in items))
            }

        if failure_origins:
            origin_builds = {
                b.id: b
                for b in Build.query.filter(
                    Build.id.in_(frozenset(failure_origins.values()))
                )
            }
        else:
            origin_builds = {}

        results = [
            {
                "hash": i.hash,
                "name": i.name,
                "runs": [
                    {
                        "id": UUID(e[0]),
                        "job_id": UUID(e[1]),
                        "duration": int(e[2]),
                        "result": Result(int(e[3])),
                    }
                    for e in i.runs
                ],
                "build": builds.get(getattr(i, "build_id", None)),
                "origin_build": origin_builds.get(failure_origins.get(i.hash)),
                "result": aggregate_result(Result(int(e[3])) for e in i.runs),
            }
            for i in items
        ]
        if many:
            return results
        return results[0]


class TestCaseSummarySchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.Str(required=True)
    hash = fields.Str(dump_only=True)
    result = ResultField(required=True)
    duration = fields.Number()
    job = fields.Nested(JobSchema, required=True)


class TestCaseSchema(TestCaseSummarySchema):
    message = fields.Str(required=False)
