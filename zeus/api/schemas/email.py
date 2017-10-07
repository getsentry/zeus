from marshmallow import Schema, fields


class EmailSchema(Schema):
    id = fields.UUID(dump_only=True)
    email = fields.Str()
    verified = fields.Bool(default=False)
