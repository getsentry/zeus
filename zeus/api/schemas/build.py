from marshmallow import Schema, fields, pre_dump

from .fields import ResultField, StatusField
from .source import SourceSchema


class CoverageStatsSchema(Schema):
    lines_covered = fields.Number()
    lines_uncovered = fields.Number()
    diff_lines_covered = fields.Number()
    diff_lines_uncovered = fields.Number()


# should be "dumped" with a list of ItemStat instances
class StatsSchema(Schema):
    coverage = fields.Nested(CoverageStatsSchema(), dump_only=True)

    @pre_dump
    def process_stats(self, data):
        return {
            'coverage':
                {
                    s.name.split('coverage.', 1)[1]: s.value
                    for s in data if s.name.startswith('coverage.')
                }
        }


class BuildSchema(Schema):
    id = fields.UUID(dump_only=True)
    number = fields.Number(dump_only=True)
    created_at = fields.DateTime(attribute="date_created", dump_only=True)
    started_at = fields.DateTime(attribute="date_started")
    finished_at = fields.DateTime(attribute="date_finished")
    status = StatusField()
    result = ResultField()
    source = fields.Nested(SourceSchema(), dump_only=True)
    stats = fields.Nested(StatsSchema(), dump_only=True)
