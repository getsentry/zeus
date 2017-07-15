from marshmallow import Schema, fields

from .organization import OrganizationSchema
from .repository import RepositorySchema


class ProjectSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.Str()
    organization = fields.Nested(OrganizationSchema())
    repository = fields.Nested(RepositorySchema())
    created_at = fields.DateTime(attribute='date_created', dump_only=True)
