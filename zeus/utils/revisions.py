from flask import current_app

from zeus.exceptions import UnknownRevision
from zeus.models import Repository, Revision
from zeus.vcs import vcs_client


def identify_revision(
    repository: Repository, ref: str, with_vcs: bool = True
) -> Revision:
    """
    Attempt to transform a a commit-like reference into a valid revision.
    """
    # try to find it from the database first
    if len(ref) == 40:
        revision = (
            Revision.query.unrestricted_unsafe()
            .filter(Revision.repository_id == repository.id, Revision.sha == ref)
            .first()
        )
        if revision:
            return revision

    if not with_vcs:
        raise UnknownRevision

    result = vcs_client.resolve(repository.id, ref=ref)

    revision = (
        Revision.query.unrestricted_unsafe()
        .filter(Revision.repository_id == repository.id, Revision.sha == result["sha"])
        .first()
    )
    if not revision:
        current_app.logger.error(
            "revision %s (repo_id=%s) found, but not present in database",
            result["sha"],
            repository.id,
        )
        raise UnknownRevision

    return revision
