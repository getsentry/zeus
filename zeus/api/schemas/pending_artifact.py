# from werkzeug.datastructures import FileStorage

from marshmallow import Schema, fields, post_load

from zeus.models import PendingArtifact

from .fields import FileField


class PendingArtifactSchema(Schema):
    id = fields.UUID(dump_only=True)
    provider = fields.Str()
    external_build_id = fields.Str()
    external_job_id = fields.Str()
    hook_id = fields.Str()
    # name can be inferred from file
    name = fields.Str(required=False)
    type = fields.Str(required=False)
    # XXX(dcramer): cant find a way to get marshmallow to handle request.files
    file = FileField(required=False)

    @post_load(pass_many=False)
    def build_instance(self, data, **kwargs):
        return PendingArtifact(**data)
