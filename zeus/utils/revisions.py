from zeus.config import redis
from zeus.exceptions import UnknownRepositoryBackend
from zeus.models import Repository, Revision
from zeus.vcs.base import UnknownRevision


def identify_revision(repository: Repository, treeish: str):
    """
    Attempt to transform a a commit-like reference into a valid revision.
    """
    # try to find it from the database first
    if len(treeish) == 40:
        revision = Revision.query.filter(
            Revision.repository_id == repository.id, Revision.sha == treeish
        ).first()
        if revision:
            return revision

    try:
        vcs = repository.get_vcs()
    except UnknownRepositoryBackend:
        return None

    vcs.ensure(update_if_exists=False)

    lock_key = "sync_repo:{repo_id}".format(repo_id=repository.id)
    # lock this update to avoild piling up duplicate fetch/save calls
    with redis.lock(lock_key):
        try:
            commit = next(vcs.log(parent=treeish, limit=1))
        except UnknownRevision:
            vcs.update()
            commit = next(vcs.log(parent=treeish, limit=1))

        revision, _ = commit.save(repository)

    return revision
