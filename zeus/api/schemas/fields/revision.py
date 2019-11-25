from flask import current_app
from marshmallow import fields
from marshmallow.exceptions import ValidationError

from zeus.utils import revisions
from zeus.vcs.base import UnknownRevision


class RevisionRefField(fields.Str):
    def __init__(self, validate_ref=True, resolve_to=None, *args, **kwargs):
        self.validate_ref = validate_ref
        self.resolve_to = resolve_to
        super().__init__(*args, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        repo = self.context.get("repository")
        if not repo:
            return value

        if not self.validate_ref and not self.resolve_to:
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
            if self.resolve_to:
                # XXX(dcramer): we'd prefer to make this a compound field
                # but Marshmallow wont let us bind this
                self.context["resolved_{}".format(self.resolve_to)] = revision
        return value
