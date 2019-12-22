from marshmallow import Schema, fields, post_load, post_dump

from zeus.models import Build, Hook

from .author import AuthorSchema
from .fields import ResultField, RevisionRefField, StatusField
from .repository import RepositorySchema
from .revision import RevisionSchema
from .stats import StatsSchema


class BuildSchema(Schema):
    id = fields.UUID(dump_only=True)
    number = fields.Integer(dump_only=True)
    label = fields.Str()
    created_at = fields.DateTime(attribute="date_created", dump_only=True)
    started_at = fields.DateTime(attribute="date_started", dump_only=True)
    finished_at = fields.DateTime(attribute="date_finished", dump_only=True)
    status = StatusField(dump_only=True)
    result = ResultField(dump_only=True)
    stats = fields.Nested(StatsSchema(), dump_only=True)
    provider = fields.Str(dump_only=True)
    external_id = fields.Str(dump_only=True)
    url = fields.Str(dump_only=True)
    repository = fields.Nested(
        RepositorySchema(exclude=("latest_build",)), dump_only=True
    )
    author = fields.Nested(AuthorSchema())
    revision = fields.Nested(RevisionSchema())
    ref = RevisionRefField(dump_only=True)

    @post_dump(pass_many=False)
    def build_output(self, data, many, **kwargs):
        if not data.get("label"):
            data["label"] = "unknown build"
        return data


class BuildCreateSchema(Schema):
    ref = RevisionRefField(validate_ref=False, required=True, resolve_to="revision")
    author = fields.Nested(AuthorSchema(), required=False)
    label = fields.Str(required=False)
    hook_id = fields.Str(required=False)
    provider = fields.Str(required=False)
    external_id = fields.Str(required=False)
    url = fields.Str(allow_none=True, required=False)

    @post_load(pass_many=False)
    def build_instance(self, data, **kwargs):
        revision = self.context.get("resolved_revision")
        build = Build(
            repository=self.context.get("repository"),
            revision_sha=revision.sha if revision else None,
            **data
        )
        if build.data is None:
            build.data = {}
        build.data["required_hook_ids"] = Hook.get_required_hook_ids(
            build.repository.id
        )
        if not build.label and revision:
            build.label = revision.message.split("\n")[0]
        if not build.author_id and revision:
            build.author_id = revision.author_id
        return build

    @post_dump(pass_many=True)
    def build_output(self, data, many, **kwargs):
        if not data.get("label"):
            data["label"] = "unknown build"
        return data
