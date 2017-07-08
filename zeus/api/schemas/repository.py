from marshmallow import Schema, fields


class RepositorySchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.Str()
    url = fields.Str()
    provider = fields.Str()
    created_at = fields.DateTime(attribute="date_created", dump_only=True)
