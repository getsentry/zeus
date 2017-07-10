from marshmallow import Schema, fields


class AuthorSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.Str()
    email = fields.Str()
    created_at = fields.DateTime(attribute="date_created", dump_only=True)
