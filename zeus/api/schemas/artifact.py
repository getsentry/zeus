# from werkzeug.datastructures import FileStorage

from marshmallow import Schema, fields, post_load

from zeus.models import Artifact


class File(fields.Field):
    def _serialize(self, value, attr, obj):
        if value is None:
            return None
        return {'name': value.filename}

    def _deserialize(value, attr, data):
        if value is None:
            return None
        return value


class ArtifactSchema(Schema):
    id = fields.UUID(dump_only=True)
    # name can be inferred from file
    name = fields.Str(required=False)
    type = fields.Str(required=False)
    # XXX(dcramer): cant find a way to get marshmallow to handle request.files
    file = File(required=False)
    created_at = fields.DateTime(attribute="date_created", dump_only=True)

    @post_load
    def build_instance(self, data):
        return Artifact(**data)
