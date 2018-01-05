from marshmallow import Schema, fields


class BundleAssetSchema(Schema):
    name = fields.Str(required=True)
    size = fields.Int()


class BundleSchema(Schema):
    id = fields.UUID(dump_only=True)
    job_id = fields.UUID(dump_only=True)
    name = fields.Str(required=True)
    assets = fields.List(fields.Nested(BundleAssetSchema))
