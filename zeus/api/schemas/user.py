from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.UUID(dump_only=True)
    email = fields.Str()
    created_at = fields.DateTime(attribute="date_created", dump_only=True)
