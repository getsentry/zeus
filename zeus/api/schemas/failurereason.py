from marshmallow import Schema, fields


class FailureReasonSchema(Schema):
    reason = fields.Str()
