from marshmallow import Schema, fields

from .repository import RepositorySchema


class ProjectSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.Str()
    repository = fields.Nested(RepositorySchema())
    created_at = fields.DateTime(attribute='date_created', dump_only=True)
