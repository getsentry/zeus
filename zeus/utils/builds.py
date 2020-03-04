from functools import reduce
from itertools import groupby
from operator import and_, or_
from typing import Any, List, Mapping, Tuple
from sqlalchemy.orm import joinedload, subqueryload_all

from zeus.constants import Status, Result
from zeus.models import Build, Revision


def merge_builds(target: Build, build: Build, with_relations=True) -> Build:
    # explicitly unset the default id as target should begin as an empty instance
    target.id = None

    # Store the original build so we can retrieve its ID or number later, or
    # show a list of all builds in the UI
    target.original.append(build)

    # These properties should theoretically always be the same within a build
    # group, so merging is not necessary.  We assign here so the initial build
    # gets populated.
    # XXX(dcramer): this is unsafe
    if with_relations:
        target.revision = build.revision
    #     target.authors = list(set(target.authors + build.authors))
    if build.revision_sha:
        target.revision_sha = build.revision_sha
    if not target.ref:
        target.ref = build.ref
    if not target.label:
        target.label = build.label

    # Merge properties, if they already exist.  In the first run, everything
    # will be empty, since every group is initialized with an empty build.
    # Afterwards, we always use the more extreme value (e.g. earlier start
    # date or worse result).
    if with_relations:
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
    build_group: Tuple[Any, List[Build]],
    required_hook_ids: List[str] = None,
    with_relations=True,
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

    return reduce(
        lambda *x: merge_builds(x[0], x[1], with_relations=with_relations),
        latest_builds,
        build,
    )


def fetch_builds_for_revisions(
    revisions: List[Revision], with_relations=True
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
                Build.repository_id == revision.repository_id,
                Build.revision_sha == revision.sha,
            )
        )

    base_qs = Build.query
    if with_relations:
        base_qs = base_qs.options(
            joinedload("revision"),
            subqueryload_all("authors"),
            subqueryload_all("revision.authors"),
            subqueryload_all("stats"),
        )

    builds = list(
        (base_qs.filter(reduce(or_, lookups)).order_by(Build.revision_sha))  # NOQA
    )
    build_groups = groupby(
        builds, lambda build: (build.repository_id, build.revision_sha)
    )
    required_hook_ids = set()
    for build in builds:
        required_hook_ids.update(build.data.get("required_hook_ids") or ())
    return [
        (
            ident,
            merge_build_group(
                list(group), required_hook_ids, with_relations=with_relations
            ),
        )
        for ident, group in build_groups
    ]


def fetch_build_for_revision(revision: Revision, with_relations=True) -> Build:
    builds = fetch_builds_for_revisions([revision], with_relations=with_relations)
    if len(builds) < 1:
        return None

    return builds[0][1]
