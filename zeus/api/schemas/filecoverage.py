from marshmallow import Schema, fields


class FileCoverageSchema(Schema):
    filename = fields.Str()
    data = fields.Str()
    lines_covered = fields.Number()
    lines_uncovered = fields.Number()
    diff_lines_covered = fields.Number()
    diff_lines_uncovered = fields.Number()
