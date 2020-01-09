from dataclasses import dataclass
from typing import List, Tuple

from zeus.exceptions import UnknownRevision
from zeus.models import Repository, Revision
from zeus.vcs import vcs_client


@dataclass
class RevisionResult:
    sha: str
    message: str
    author: str
    author_date: str
    committer: str
    committer_date: str
    parents: List[str]
    authors: List[Tuple[str, str]]


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

    result = next(vcs_client.log(repository.id, parent=ref, limit=1))
    revision = Revision.query.filter(
        Revision.repository_id == repository.id, Revision.sha == result["sha"]
    ).first()
    if not revision:
        raise UnknownRevision
