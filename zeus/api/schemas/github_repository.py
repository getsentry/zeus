from marshmallow import Schema, fields


class GitHubRepositorySchema(Schema):
    name = fields.Str()
