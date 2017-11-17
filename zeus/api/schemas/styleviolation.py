from marshmallow import Schema, fields

from .fields import SeverityField


class StyleViolationSchema(Schema):
    id = fields.UUID(dump_only=True)
    job_id = fields.UUID(dump_only=True)
    filename = fields.Str(required=True)
    severity = SeverityField(required=True)
    message = fields.Str(required=True)
    lineno = fields.Number(required=False)
    colno = fields.Number(required=False)
    source = fields.Str(required=False)
