from marshmallow import Schema, fields

from zeus.models import RepositoryBackend

from .fields import EnumField


class RepositorySchema(Schema):
    id = fields.UUID(dump_only=True)
    owner_name = fields.Str()
    name = fields.Str()
    url = fields.Str()
    provider = fields.Str()
    backend = EnumField(RepositoryBackend)
    admin = fields.Bool()
    created_at = fields.DateTime(
        attribute='date_created',
        dump_only=True,
    )
    full_name = fields.Method('get_full_name')

    def get_full_name(self, obj):
        return '{}/{}/{}'.format(obj.provider, obj.owner_name, obj.name)
