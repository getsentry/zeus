from flask import current_app
from marshmallow import fields
from marshmallow.exceptions import ValidationError

from zeus.utils import revisions
from zeus.vcs.base import UnknownRevision


class RevisionRefField(fields.Str):
    def _deserialize(self, value, attr, data, **kwargs):
        repo = self.context.get("repository")
        if repo:
            try:
                revision = revisions.identify_revision(repo, value)
            except UnknownRevision as e:
                current_app.logger.warn("invalid ref received", exc_info=True)
                raise ValidationError("unknown revision: {}".format(value)) from e

            return revision.sha

        return value
