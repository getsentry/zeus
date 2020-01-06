from zeus.exceptions import UnknownRepositoryBackend
from zeus.models import Repository, Revision
from zeus.vcs.base import UnknownRevision


def identify_revision(
    repository: Repository, ref: str, with_vcs: bool = True
) -> Revision:
    """
    Attempt to transform a a commit-like reference into a valid revision.
    """
    # try to find it from the database first
    if len(ref) == 40:
        revision = Revision.query.filter(
            Revision.repository_id == repository.id, Revision.sha == ref
        ).first()
        if revision:
            return revision

    if not with_vcs:
        raise UnknownRevision

    try:
        vcs = repository.get_vcs()
    except UnknownRepositoryBackend:
        raise UnknownRevision

    vcs.ensure(update_if_exists=False)

    try:
        commit = next(vcs.log(parent=ref, limit=1))
    except UnknownRevision:
        vcs.update()
        commit = next(vcs.log(parent=ref, limit=1))

    revision, _ = commit.save(repository)

    return revision
