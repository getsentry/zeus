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
    created_at = fields.DateTime(
        attribute='date_created',
        dump_only=True,
    )


class GitHubRepositorySchema(Schema):
    id = fields.UUID(dump_only=True)
    github_name = fields.Str(load_from='github.name')
