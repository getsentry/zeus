from sqlalchemy.orm import joinedload, undefer
from zeus.models import Source, Revision

from .base_revision import BaseRevisionResource
from ..schemas import SourceSchema

source_schema = SourceSchema(strict=True)


class RevisionSourceResource(BaseRevisionResource):

    def get(self, revision: Revision):
        """
        Return a source for the given revision.
        """
        source = Source.query.options(
            joinedload("patch"), undefer("patch.diff")
        ).filter(
            Source.revision == revision, Source.patch == None  # NoQA
        ).one_or_none()
        if source is None:
            return self.not_found()

        return self.respond_with_schema(source_schema, source)
