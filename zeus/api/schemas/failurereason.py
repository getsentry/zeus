from marshmallow import Schema, fields, pre_dump
from uuid import UUID

from zeus.api.schemas.fields.enum import EnumField
from zeus.models import FailureReason


class ReasonField(EnumField):
    enum = FailureReason.Reason


class FailureReasonSchema(Schema):
    reason = ReasonField()


class ExecutionSchema(Schema):
    id = fields.UUID(dump_only=True)
    job_id = fields.UUID(required=True)


class AggregateFailureReasonSchema(Schema):
    reason = ReasonField()
    runs = fields.List(fields.Nested(ExecutionSchema), required=True)

    @pre_dump
    def process_aggregates(self, data, **kwargs):
        return {
            "reason": data.reason,
            "runs": [
                {"id": UUID(e[0]), "job_id": UUID(e[1]) if e[1] else None}
                for e in sorted(
                    data.runs, key=lambda e: UUID(e[1]) if e[1] else 0, reverse=True
                )
            ],
        }
