from marshmallow import Schema, fields


class IdentitySchema(Schema):
    id = fields.UUID(dump_only=True)
    external_id = fields.Str(dump_only=True)
    provider = fields.Str(dump_only=True)
    scopes = fields.List(fields.Str, dump_only=True)
    created_at = fields.DateTime(attribute="date_created", dump_only=True)
