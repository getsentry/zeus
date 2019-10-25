from flask import current_app
from marshmallow import fields
from marshmallow.exceptions import ValidationError

from zeus.utils import revisions
from zeus.vcs.base import UnknownRevision


class RevisionRefField(fields.Str):
    def __init__(self, validate_ref=True, *args, **kwargs):
        self.validate_ref = validate_ref
        super().__init__(*args, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        repo = self.context.get("repository")
        if repo and self.validate_ref:
            try:
                revision = revisions.identify_revision(repo, value)
            except UnknownRevision as e:
                current_app.logger.warn("invalid ref received", exc_info=True)
                raise ValidationError("unknown revision: {}".format(value)) from e

            return revision.sha

        return value
