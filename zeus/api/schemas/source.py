from marshmallow import Schema, fields

from .author import AuthorSchema
from .revision import RevisionSchema


class SourceSchema(Schema):
    id = fields.UUID(dump_only=True)
    revision = fields.Nested(RevisionSchema())
    author = fields.Nested(AuthorSchema(), dump_only=True)
    created_at = fields.DateTime(attribute="date_created", dump_only=True)
    diff = fields.Function(lambda o: o.generate_diff(), dump_only=True)


class SourceCreateSchema(Schema):
    revision_sha = fields.Str(required=True)
    author = fields.Nested(AuthorSchema())
