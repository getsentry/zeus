from marshmallow import Schema, fields


class TokenSchema(Schema):
    id = fields.UUID(dump_only=True)
    key = fields.Str(dump_only=True)
