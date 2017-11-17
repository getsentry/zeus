from collections import defaultdict
from marshmallow import Schema, fields, pre_dump


class CoverageStatsSchema(Schema):
    lines_covered = fields.Integer()
    lines_uncovered = fields.Integer()
    diff_lines_covered = fields.Integer()
    diff_lines_uncovered = fields.Integer()


class TestStatsSchema(Schema):
    count = fields.Integer()
    failures = fields.Integer()
    duration = fields.Number()


class StyleViolationsSchema(Schema):
    count = fields.Integer()


# should be "dumped" with a list of ItemStat instances
class StatsSchema(Schema):
    coverage = fields.Nested(CoverageStatsSchema(), dump_only=True)
    tests = fields.Nested(TestStatsSchema(), dump_only=True)
    style_violations = fields.Nested(StyleViolationsSchema(), dump_only=True)

    @pre_dump
    def process_stats(self, data):
        result = defaultdict(lambda: defaultdict(int))
        for stat in data:
            bits = stat.name.split('.', 1)
            if len(bits) != 2:
                continue
            result[bits[0]][bits[1]] = stat.value
        return result
