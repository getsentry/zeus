from marshmallow import Schema, fields, post_load

from zeus.models import ChangeRequest

from .author import AuthorSchema
from .fields import RevisionRefField
from .revision import RevisionSchema


class ChangeRequestSchema(Schema):
    id = fields.UUID(dump_only=True)
    number = fields.Integer(dump_only=True)
    message = fields.Str()
    author = fields.Nested(AuthorSchema(), dump_only=True)
    head_revision_sha = RevisionRefField(
        validate=False, allow_none=True, load_only=True
    )
    parent_revision_sha = RevisionRefField(
        validate=False, required=True, load_only=True
    )
    head_revision = fields.Nested(RevisionSchema(), allow_none=True, dump_only=True)
    parent_revision = fields.Nested(RevisionSchema(), required=True, dump_only=True)
    provider = fields.Str(dump_only=True)
    external_id = fields.Str(dump_only=True)
    url = fields.Str(dump_only=True)
    created_at = fields.DateTime(attribute="date_created", dump_only=True)

    @post_load(pass_many=False)
    def make_hook(self, data, **kwargs):
        if self.context.get("change_request"):
            cr = self.context["change_request"]
            for key, value in data.items():
                if getattr(cr, key) != value:
                    setattr(cr, key, value)
        else:
            cr = ChangeRequest(**data)
        return cr


class ChangeRequestCreateSchema(Schema):
    author = fields.Nested(AuthorSchema(), allow_none=True)
    head_revision_sha = RevisionRefField(
        validate=False, allow_none=True, load_only=True
    )
    parent_revision_sha = RevisionRefField(
        validate=False, required=True, load_only=True
    )
    provider = fields.Str(required=True)
    message = fields.Str(required=True)
    external_id = fields.Str(required=True)
    url = fields.Str(allow_none=True)
    created_at = fields.DateTime(attribute="date_created")

    @post_load(pass_many=False)
    def make_hook(self, data, **kwargs):
        return ChangeRequest(**data)
