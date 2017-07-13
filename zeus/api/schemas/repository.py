from marshmallow import Schema, fields

from zeus.models import RepositoryBackend

from .fields import EnumField


class RepositorySchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.Str()
    url = fields.Str()
    backend = EnumField(RepositoryBackend)
    created_at = fields.DateTime(attribute='date_created', dump_only=True)
