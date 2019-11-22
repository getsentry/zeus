from flask import current_app
from marshmallow import fields
from marshmallow.exceptions import ValidationError

from zeus.utils import revisions
from zeus.vcs.base import UnknownRevision


class RevisionRefField(fields.Str):
    def __init__(self, validate_ref=True, sha_field=None, *args, **kwargs):
        self.validate_ref = validate_ref
        self.sha_field = sha_field
        super().__init__(*args, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        repo = self.context.get("repository")
        if not repo:
            return value

        try:
            revision = revisions.identify_revision(
                repo, value, with_vcs=self.validate_ref
            )
        except UnknownRevision as e:
            if self.validate_ref:
                current_app.logger.warn("invalid ref received", exc_info=True)
                raise ValidationError("unknown revision: {}".format(value)) from e
        else:
            if self.sha_field:
                data[self.sha_field] = revision.sha

        return value
