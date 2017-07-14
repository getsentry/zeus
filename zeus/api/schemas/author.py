from marshmallow import Schema, fields


class AuthorSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.String()
    email = fields.String(required=False)
