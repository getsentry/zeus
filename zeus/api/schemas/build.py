from marshmallow import Schema, fields

from .fields import ResultField, StatusField
from .source import SourceSchema


class BuildSchema(Schema):
    id = fields.UUID(dump_only=True)
    number = fields.Number(dump_only=True)
    created_at = fields.DateTime(attribute="date_created", dump_only=True)
    started_at = fields.DateTime(attribute="date_started")
    finished_at = fields.DateTime(attribute="date_finished")
    status = StatusField()
    result = ResultField()
    source = fields.Nested(SourceSchema(), dump_only=True)
