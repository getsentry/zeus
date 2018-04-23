# from werkzeug.datastructures import FileStorage

from marshmallow import Schema, fields, post_load

from zeus.models import Artifact

from .fields import FileField, StatusField


class ArtifactSchema(Schema):
    id = fields.UUID(dump_only=True)
    # name can be inferred from file
    name = fields.Str(required=False)
    type = fields.Str(required=False)
    # XXX(dcramer): cant find a way to get marshmallow to handle request.files
    file = FileField(required=False)
    status = StatusField(dump_only=True)
    created_at = fields.DateTime(attribute="date_created", dump_only=True)
    started_at = fields.DateTime(attribute="date_started", allow_none=True)
    finished_at = fields.DateTime(attribute="date_finished", allow_none=True)
    updated_at = fields.DateTime(attribute="date_updated", dump_only=True)
    download_url = fields.Method("get_download_url")

    def get_download_url(self, obj):
        return "/api/repos/%s/%s/%s/builds/%s/jobs/%s/artifacts/%s/download" % (
            obj.job.build.source.repository.provider,
            obj.job.build.source.repository.owner_name,
            obj.job.build.source.repository.name,
            obj.job.build.number,
            obj.job.number,
            obj.id,
        )

    @post_load
    def build_instance(self, data):
        return Artifact(**data)
