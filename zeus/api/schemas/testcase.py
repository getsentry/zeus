from collections import defaultdict
from marshmallow import Schema, fields, pre_dump
from typing import List, Mapping
from uuid import UUID

from zeus.config import db
from zeus.constants import Result, Status
from zeus.exceptions import UnknownRepositoryBackend
from zeus.models import Build, Job, Source, TestCase
from zeus.utils.aggregation import aggregate_result
from zeus.vcs.base import UnknownRevision

from .build import BuildSchema
from .fields import ResultField
from .job import JobSchema


def find_failure_origins(build: Build, test_failures: List[str]) -> Mapping[str, UUID]:
    """
    Attempt to find originating causes of failures.

    Returns a mapping of {TestCase.hash: Job}.
    """
    if not test_failures:
        return {}

    source = build.source
    repo = build.repository
    try:
        vcs = repo.get_vcs()
    except UnknownRepositoryBackend:
        valid_revisions = []
    else:
        try:
            valid_revisions = [
                c.sha for c in vcs.log(limit=100, parent=source.revision_sha)
            ]
        except UnknownRevision:
            valid_revisions = []

    filters = [
        Build.repository_id == build.repository_id,
        Build.status == Status.finished,
        Source.id != source.id,
        Source.patch_id == None,  # NOQA
    ]
    if valid_revisions:
        filters.extend(
            [
                Source.revision_sha.in_(valid_revisions),
                Source.repository_id == build.repository_id,
            ]
        )

    # NOTE(dcramer): many of these queries ignore tenant constraints
    # find any existing failures in the previous runs
    # to do this we first need to find the last passing build
    last_pass = (
        db.session.query(Source.id, Source.date_created)
        .join(Build, Source.id == Build.source_id)
        .filter(
            Build.result == Result.passed,
            Source.date_created <= source.date_created,
            Build.date_created <= build.date_created,
            *filters,
        )
        .order_by(Source.date_created.desc())
        .first()
    )

    if last_pass:
        last_pass_source_id, last_pass_date = last_pass

        # We have to query all runs between build and last_pass. Because we're
        # paranoid about performance, we limit this to 100 results.
        previous_build_ids = [
            r
            for r, in db.session.query(Build.id)
            .join(Source, Source.id == Build.source_id)
            .filter(
                Build.result == Result.failed,
                Build.date_created >= last_pass_date,
                Source.date_created >= last_pass_date,
                Source.id != last_pass_source_id,
                *filters,
            )
            .order_by(Source.date_created.desc())[:100]
        ]
    else:
        previous_build_ids = [
            r
            for r, in db.session.query(Build.id)
            .join(Source, Source.id == build.source_id)
            .filter(Build.result == Result.failed, *filters)
            .order_by(Source.date_created.desc())[:100]
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

    failures_at_build = dict()
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
        BuildSchema(exclude=("repository", "source", "stats")), required=False
    )
    origin_build = fields.Nested(
        BuildSchema(exclude=("repository", "source", "stats")), required=False
    )

    @pre_dump(pass_many=True)
    def process_aggregates(self, data, many):
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
