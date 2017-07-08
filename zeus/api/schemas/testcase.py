from marshmallow import Schema, fields


class TestCaseSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.Str()
    duration = fields.Number()
    result = fields.Str()
