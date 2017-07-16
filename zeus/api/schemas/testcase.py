from marshmallow import Schema, fields

from .fields import ResultField


class TestCaseSchema(Schema):
    id = fields.UUID(dump_only=True)
    job_id = fields.UUID(dump_only=True)
    name = fields.Str(required=True)
    duration = fields.Number(required=False)
    result = ResultField(required=True)
    message = fields.Str(required=False)


class TestCaseSummarySchema(Schema):
    id = fields.UUID(dump_only=True)
    job_id = fields.UUID(dump_only=True)
    name = fields.Str()
    duration = fields.Number()
    result = ResultField()
