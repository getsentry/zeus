from zeus.config import db
from zeus.db.mixins import RepositoryBoundMixin, StandardAttributes
from zeus.db.types import GUID
from zeus.db.utils import get_or_create, model_repr


class RepositoryRef(RepositoryBoundMixin, StandardAttributes, db.Model):
    name = db.Column(db.String)

    __table_args__ = (
        db.UniqueConstraint("repository_id", "name", name="unq_repository_ref"),
    )
    __tablename__ = "repository_ref"
    __repr__ = model_repr("repository_id", "name")

    @classmethod
    def get(cls, repository_id: GUID, name: str):
        return get_or_create(cls, where={"repository_id": repository_id, "name": name})[
            0
        ]
