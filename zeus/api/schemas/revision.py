from marshmallow import Schema, fields


class RevisionSchema(Schema):
    id = fields.UUID(dump_only=True)
    sha = fields.Str()
    message = fields.Str()
    created_at = fields.DateTime(attribute="date_created", dump_only=True)
