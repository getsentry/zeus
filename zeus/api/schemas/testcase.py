from marshmallow import Schema, fields, pre_dump
from uuid import UUID

from zeus.constants import Result
from zeus.utils.aggregation import aggregate_result

from .fields import ResultField
from .job import JobSchema


class ExecutionSchema(Schema):
    id = fields.UUID(dump_only=True)
    result = ResultField(required=True)
    duration = fields.Number()
    job_id = fields.UUID(required=True)


class AggregateTestCaseSummarySchema(Schema):
    name = fields.Str(required=True)
    hash = fields.Str(dump_only=True)
    runs = fields.List(fields.Nested(ExecutionSchema), required=True)
    result = ResultField(required=True)

    @pre_dump
    def process_aggregates(self, data):
        return {
            "name": data.name,
            "runs": [
                {
                    "id": UUID(e[0]),
                    "job_id": UUID(e[1]),
                    "duration": int(e[2]),
                    "result": Result(int(e[3])),
                }
                for e in data.runs
            ],
            "result": aggregate_result(Result(int(e[3])) for e in data.runs),
        }


class AggregateTestCaseSummarySchema(AggregateTestCaseSummarySchema):
    message = fields.Str(required=False)


class TestCaseSummarySchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.Str(required=True)
    hash = fields.Str(dump_only=True)
    result = ResultField(required=True)
    duration = fields.Number()
    job = fields.Nested(JobSchema, required=True)


class TestCaseSchema(TestCaseSummarySchema):
    message = fields.Str(required=False)
