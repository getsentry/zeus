from marshmallow import Schema, fields


# TODO(dcramer): sort out file storage
class ArtifactSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.Str()
    type = fields.Str()
    created_at = fields.DateTime(attribute="date_created", dump_only=True)
