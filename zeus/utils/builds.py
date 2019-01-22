from functools import reduce
from itertools import groupby
from operator import and_, or_
from typing import Any, List, Mapping, Tuple
from sqlalchemy.orm import contains_eager, subqueryload_all

from zeus.constants import Status, Result
from zeus.models import Build, Revision, Source


def merge_builds(target: Build, build: Build) -> Build:
    # explicitly unset the default id as target should begin as an empty instance
    target.id = None

    # Store the original build so we can retrieve its ID or number later, or
    # show a list of all builds in the UI
    target.original.append(build)

    # These properties should theoretically always be the same within a build
    # group, so merging is not necessary.  We assign here so the initial build
    # gets populated.
    target.source = build.source
    target.label = build.source.revision.message

    # Merge properties, if they already exist.  In the first run, everything
    # will be empty, since every group is initialized with an empty build.
    # Afterwards, we always use the more extreme value (e.g. earlier start
    # date or worse result).
    target.stats = target.stats + build.stats if target.stats else build.stats
    target.status = (
        Status(max(target.status.value, build.status.value))
        if target.status
        else build.status
    )
    target.result = (
        Result(max(target.result.value, build.result.value))
        if target.result
        else build.result
    )
    target.date_started = (
        min(target.date_started, build.date_started)
        if target.date_started and build.date_started
        else target.date_started or build.date_started
    )
    target.date_finished = (
        max(target.date_finished, build.date_finished)
        if target.date_finished and build.date_finished
        else target.date_finished or build.date_finished
    )
    target.provider = (
        "%s, %s" % (target.provider, build.provider)
        if target.provider
        else build.provider
    )

    # NOTE: The build number is not merged, as it would not convey any meaning
    # in the context of a build group.  In that fashion, build numbers should
    # not be used in the UI, until we create a better interface.

    # NOTE: We do not merge data here, as it is not really used in the UI
    # If there is an actual use for data, then it should be merged or appended

    return target


def merge_build_group(
    build_group: Tuple[Any, List[Build]], required_hook_ids: List[str] = None
) -> Build:
    # XXX(dcramer): required_hook_ids is still dirty here, but its our simplest way
    # to get it into place
    grouped_builds = groupby(
        build_group, lambda build: (str(build.hook_id), build.provider)
    )
    latest_builds = [
        max(build, key=lambda build: build.number) for _, build in grouped_builds
    ]

    build = Build()
    build.original = []
    if set(required_hook_ids or ()).difference(
        set(str(b.hook_id) for b in build_group)
    ):
        build.result = Result.failed

    return reduce(merge_builds, latest_builds, build)


def fetch_builds_for_revisions(
    revisions: List[Revision], required_hook_ids: List[str] = None
) -> Mapping[str, Build]:
    # we query extra builds here, but its a lot easier than trying to get
    # sqlalchemy to do a ``select (subquery)`` clause and maintain tenant
    # constraints
    if not revisions:
        return {}

    lookups = []
    for revision in revisions:
        lookups.append(
            and_(
                Source.repository_id == revision.repository_id,
                Source.revision_sha == revision.sha,
            )
        )

    builds = (
        Build.query.options(
            contains_eager("source"),
            contains_eager("source").joinedload("author"),
            contains_eager("source").joinedload("revision", innerjoin=True),
            subqueryload_all("stats"),
        )
        .join(Source, Build.source_id == Source.id)
        .filter(Source.patch_id == None, reduce(or_, lookups))  # NOQA
        .order_by(Source.revision_sha)
    )
    build_groups = groupby(
        builds, lambda build: (build.source.repository_id, build.source.revision_sha)
    )
    return [
        (ident, merge_build_group(list(group), required_hook_ids))
        for ident, group in build_groups
    ]


def fetch_build_for_revision(revision: Revision) -> Build:
    source = (
        Source.query.unrestricted_unsafe()
        .filter(
            Source.revision_sha == revision.sha,
            Source.repository_id == revision.repository_id,
        )
        .first()
    )
    if source:
        required_hook_ids = source.data.get("required_hook_ids") or ()
    else:
        required_hook_ids = ()

    builds = fetch_builds_for_revisions([revision], required_hook_ids)
    if len(builds) < 1:
        return None

    return builds[0][1]
