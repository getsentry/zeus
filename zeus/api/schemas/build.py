from marshmallow import Schema, fields

from .fields import ResultField, RevisionRefField, StatusField
from .repository import RepositorySchema
from .source import SourceSchema
from .stats import StatsSchema


class BuildSchema(Schema):
    id = fields.UUID(dump_only=True)
    number = fields.Integer(dump_only=True)
    label = fields.Str()
    created_at = fields.DateTime(attribute="date_created", dump_only=True)
    started_at = fields.DateTime(attribute="date_started", dump_only=True)
    finished_at = fields.DateTime(attribute="date_finished", dump_only=True)
    status = StatusField(dump_only=True)
    result = ResultField(dump_only=True)
    source = fields.Nested(SourceSchema(exclude=["diff"]), dump_only=True)
    stats = fields.Nested(StatsSchema(), dump_only=True)
    provider = fields.Str(dump_only=True)
    external_id = fields.Str(dump_only=True)
    url = fields.Str(dump_only=True)
    is_author = fields.Bool(dump_only=True)
    repository = fields.Nested(
        RepositorySchema(exclude=("latest_build",)), dump_only=True
    )


class BuildCreateSchema(Schema):
    # label is only required if they're specifying a source with a patch (which they cant do yet)
    label = fields.Str(required=False)
    provider = fields.Str()
    external_id = fields.Str()
    url = fields.Str(allow_none=True)
    ref = RevisionRefField(required=True)
