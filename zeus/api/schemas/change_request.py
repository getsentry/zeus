from marshmallow import Schema, fields, post_load

from zeus.models import ChangeRequest

from .author import AuthorSchema
from .fields import RevisionRefField
from .revision import RevisionSchema


class ChangeRequestSchema(Schema):
    id = fields.UUID(dump_only=True)
    number = fields.Integer(dump_only=True)
    message = fields.Str()
    authors = fields.List(fields.Nested(AuthorSchema()), required=False)
    parent_ref = RevisionRefField(
        validate_ref=False, required=True, resolve_to="parent_revision"
    )
    parent_revision_sha = RevisionRefField(required=True, dump_only=True)
    head_ref = RevisionRefField(
        allow_none=True, validate_ref=False, required=False, resolve_to="head_revision"
    )
    head_revision_sha = RevisionRefField(allow_none=True, dump_only=True)
    head_revision = fields.Nested(RevisionSchema(), allow_none=True, dump_only=True)
    parent_revision = fields.Nested(RevisionSchema(), required=True, dump_only=True)
    provider = fields.Str(dump_only=True)
    external_id = fields.Str(dump_only=True)
    url = fields.Str(dump_only=True)
    created_at = fields.DateTime(attribute="date_created", dump_only=True)

    @post_load(pass_many=False)
    def make_hook(self, data, **kwargs):
        parent_revision = self.context.get("resolved_parent_revision")
        head_revision = self.context.get("resolved_head_revision")
        if self.context.get("change_request"):
            cr = self.context["change_request"]
            for key, value in data.items():
                if getattr(cr, key) != value:
                    if key == "head_ref":
                        cr.head_revision_sha = (
                            head_revision.sha if head_revision else None
                        )
                    if key == "parent_ref":
                        cr.parent_revision_sha = (
                            parent_revision.sha if parent_revision else None
                        )
                    setattr(cr, key, value)
        else:
            cr = ChangeRequest(
                repository=self.context.get("repository"),
                head_revision_sha=head_revision.sha if head_revision else None,
                parent_revision_sha=parent_revision.sha if parent_revision else None,
                **data
            )
        if not cr.authors and head_revision and head_revision.authors:
            cr.authors = head_revision.authors
        return cr


class ChangeRequestCreateSchema(Schema):
    author = fields.Nested(AuthorSchema(), required=False, allow_none=True)
    authors = fields.List(
        fields.Nested(AuthorSchema()), required=False, allow_none=True
    )
    parent_ref = RevisionRefField(
        validate_ref=False, required=True, resolve_to="parent_revision"
    )
    head_ref = RevisionRefField(
        allow_none=True, validate_ref=False, required=False, resolve_to="head_revision"
    )
    provider = fields.Str(required=True)
    message = fields.Str(required=True)
    external_id = fields.Str(required=True)
    url = fields.Str(allow_none=True)
    created_at = fields.DateTime(attribute="date_created")

    @post_load(pass_many=False)
    def build_instance(self, data, **kwargs):
        parent_revision = self.context.get("resolved_parent_revision")
        head_revision = self.context.get("resolved_head_revision")
        cr = ChangeRequest(
            repository=self.context.get("repository"),
            head_revision_sha=head_revision.sha if head_revision else None,
            parent_revision_sha=parent_revision.sha if parent_revision else None,
            **data
        )
        if not cr.authors and head_revision and head_revision.authors:
            cr.authors = head_revision.authors
        return cr
