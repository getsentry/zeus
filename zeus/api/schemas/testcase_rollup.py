__all__ = ("TestCaseStatisticsSchema",)

from marshmallow import Schema, fields


class TestCaseStatisticsSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.Str(required=True)
    hash = fields.Str(dump_only=True)

    runs_failed = fields.Integer(dump_only=True)
    total_runs = fields.Integer(dump_only=True)
    avg_duration = fields.Integer(dump_only=True)
