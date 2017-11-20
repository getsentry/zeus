from marshmallow import Schema, fields

from .failurereason import FailureReasonSchema
from .fields import ResultField, StatusField
from .stats import StatsSchema


class JobSchema(Schema):
    id = fields.UUID(dump_only=True)
    number = fields.Integer(dump_only=True)
    created_at = fields.DateTime(attribute='date_created', dump_only=True)
    started_at = fields.DateTime(attribute='date_started', allow_none=True)
    finished_at = fields.DateTime(attribute='date_finished', allow_none=True)
    updated_at = fields.DateTime(attribute='date_updated', dump_only=True)
    label = fields.Str()
    status = StatusField()
    result = ResultField()
    stats = fields.Nested(StatsSchema(), dump_only=True)
    # XXX(dcramer): these should be dump_only in normal cases, but not via hooks
    provider = fields.Str()
    external_id = fields.Str()
    url = fields.Str(allow_none=True)
    failures = fields.List(fields.Nested(FailureReasonSchema), dump_only=True)
    allow_failure = fields.Bool(default=False)
