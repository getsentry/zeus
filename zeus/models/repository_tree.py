from typing import List

from zeus.config import db
from zeus.db.mixins import RepositoryBoundMixin
from zeus.db.types import GUID
from zeus.db.utils import model_repr
from zeus.exceptions import MissingRevision


class RepositoryTree(RepositoryBoundMixin, db.Model):
    """
    A tree is a fast-access flat mapping for a given ref.

    It, for example, lets you answer ``git log master``, where you identify
    master by name in the ``RepositoryRef`` model.

    The tree is updated on push, and will automatically rewrite relevant entries
    upon a force push, removing invalid references.

    Revisions are ordered using the ``order`` column, where the oldest item in the tree
    has the smallest ``order`` value.
    """

    ref_id = db.Column(GUID, db.ForeignKey("repository_ref.id"), primary_key=True)
    order = db.Column(db.Integer, primary_key=True)
    revision_sha = db.Column(db.String(40), db.ForeignKey("revision.sha"))

    revision = db.relationship("Revision", foreign_keys=[revision_sha])
    ref = db.relationship("RepositoryRef", foreign_keys=[ref_id])

    __tablename__ = "repository_tree"
    __table_args__ = (
        db.UniqueConstraint("ref_id", "revision_sha", name="unq_tree_revision"),
    )
    __repr__ = model_repr("repository_id", "order", "revision_sha")

    @classmethod
    def append_tree(
        cls,
        repository_id: GUID,
        ref_id: GUID,
        parent_sha: str = None,
        new_revisions: List[str] = (),
    ):
        """
        Update the cached tree for ``ref_id`` beginning at ``parent_sha``.

        ``new_revisions`` should be passed in commit order, with the oldest being
        first. Thus, given the following tree:

        A -> B -> C -> D

        If you are passing ``parent_sha=B``, ``new_revisions`` should be ``[C, D]``.

        If ``parent_sha`` does not exist, a ``MissingRevision`` exception will be
        raised.

        If ``parent_sha`` is ``None``, this will wipe the existing tree (if it exists)
        and create it from the given revisions.
        """
        if parent_sha:
            tree_base = cls.query.filter(
                cls.ref_id == ref_id, cls.revision_sha == parent_sha
            ).first()
            if not tree_base:
                if db.session.query(
                    cls.query.filter(cls.ref_id == ref_id).exists()
                ).scalar():
                    raise MissingRevision(
                        "Revision {} not found in tree".format(parent_sha),
                        sha=parent_sha,
                    )
                new_revisions = new_revisions + [parent_sha]
        else:
            tree_base = None

        with db.session.begin_nested():
            if tree_base:
                cls.query.filter(
                    cls.ref_id == ref_id, cls.order > tree_base.order
                ).delete()
                current_order = tree_base.order
            else:
                cls.query.filter(cls.ref_id == ref_id).delete()
                current_order = -1

            for revision_sha in new_revisions:
                current_order += 1
                db.session.add(
                    cls(
                        ref_id=ref_id,
                        repository_id=repository_id,
                        order=current_order,
                        revision_sha=revision_sha,
                    )
                )

    @classmethod
    def prepend_tree(
        cls,
        repository_id: GUID,
        ref_id: GUID,
        parent_sha: str = None,
        new_revisions: List[str] = (),
    ):
        """
        Update the cached tree for ``ref_id`` ending at ``parent_sha``.

        ``new_revisions`` should be passed in commit order, with the newest being
        first. Thus, given the following tree:

        A -> B -> C -> D

        If you are passing ``parent_sha=C``, ``new_revisions`` should be ``[B, A]``.
        """
        if parent_sha:
            tree_base = cls.query.filter(
                cls.ref_id == ref_id, cls.revision_sha == parent_sha
            ).first()
            if tree_base is None:
                if db.session.query(
                    cls.query.filter(cls.ref_id == ref_id).exists()
                ).scalar():
                    raise MissingRevision(
                        "Revision {} not found in tree".format(parent_sha),
                        sha=parent_sha,
                    )
                new_revisions = [parent_sha] + new_revisions
        else:
            tree_base = None

        with db.session.begin_nested():
            if tree_base:
                cls.query.filter(
                    cls.ref_id == ref_id, cls.order < tree_base.order
                ).delete()
                current_order = tree_base.order
            else:
                cls.query.filter(cls.ref_id == ref_id).delete()
                current_order = 1

            for revision_sha in new_revisions:
                current_order -= 1
                db.session.add(
                    cls(
                        ref_id=ref_id,
                        repository_id=repository_id,
                        order=current_order,
                        revision_sha=revision_sha,
                    )
                )
