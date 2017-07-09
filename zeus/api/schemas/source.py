from marshmallow import Schema, fields

from .revision import RevisionSchema


class SourceSchema(Schema):
    id = fields.UUID(dump_only=True)
    revision = fields.Nested(RevisionSchema())
    created_at = fields.DateTime(attribute="date_created", dump_only=True)
