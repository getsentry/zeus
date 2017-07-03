from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Str()
    email = fields.Str()
    created_at = fields.DateTime()
