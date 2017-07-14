from zeus.config import db
from zeus.db.mixins import RepositoryBoundMixin, StandardAttributes
from zeus.db.utils import model_repr


class Project(RepositoryBoundMixin, StandardAttributes, db.Model):
    """
    Represents a single project.
    """
    name = db.Column(db.String(200), nullable=False)

    __tablename__ = 'project'
    __table_args__ = (db.UniqueConstraint('organization_id', 'name', name='unq_project_name'), )
    __repr__ = model_repr('name')
