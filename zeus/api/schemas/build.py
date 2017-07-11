from marshmallow import Schema, fields

from .author import AuthorSchema
from .fields import ResultField, StatusField
from .source import SourceSchema
from .stats import StatsSchema


class BuildSchema(Schema):
    id = fields.UUID(dump_only=True)
    number = fields.Number(dump_only=True)
    created_at = fields.DateTime(attribute="date_created", dump_only=True)
    started_at = fields.DateTime(attribute="date_started", dump_only=True)
    finished_at = fields.DateTime(attribute="date_finished", dump_only=True)
    status = StatusField(dump_only=True)
    result = ResultField(dump_only=True)
    author = fields.Nested(AuthorSchema(), dump_only=True)
    source = fields.Nested(SourceSchema(), dump_only=True)
    stats = fields.Nested(StatsSchema(), dump_only=True)
    provider = fields.Str(dump_only=True)
    external_id = fields.Str(dump_only=True)


class BuildCreateSchema(Schema):
    author = fields.UUID()
    revision_sha = fields.Str()
    provider = fields.Str()
    external_id = fields.Str()
