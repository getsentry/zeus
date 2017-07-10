from marshmallow import Schema, fields

from .author import AuthorSchema


class RevisionSchema(Schema):
    id = fields.UUID(dump_only=True)
    sha = fields.Str()
    message = fields.Str()
    author = fields.Nested(AuthorSchema(), dump_only=True)
    created_at = fields.DateTime(attribute="date_created", dump_only=True)
