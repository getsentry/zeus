import jsonschema

from base64 import urlsafe_b64encode
from datetime import timedelta
from marshmallow import Schema, fields, post_load
from marshmallow.exceptions import ValidationError

from zeus.models import Hook
from zeus.utils import timezone

from zeus.providers import InvalidProvider, get_provider, VALID_PROVIDER_NAMES


class HookConfigField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        return dict(value) if value else {}

    def _deserialize(self, value, attr, data, **kwargs):
        provider_name = data.get("provider")
        if provider_name:
            try:
                provider_cls = get_provider(provider_name)
            except InvalidProvider:
                raise ValidationError("Invalid provider")

            try:
                provider_cls.validate_config(value)
            except jsonschema.ValidationError as e:
                raise ValidationError from e

        return value


class HookSchema(Schema):
    id = fields.UUID(dump_only=True)
    provider = fields.Str(
        validate=[fields.validate.OneOf(choices=VALID_PROVIDER_NAMES)]
    )
    provider_name = fields.Method("get_provider_name", dump_only=True)
    token = fields.Method("get_token", dump_only=True)
    secret_uri = fields.Method("get_secret_uri", dump_only=True)
    public_uri = fields.Method("get_public_uri", dump_only=True)
    is_required = fields.Boolean()
    created_at = fields.DateTime(attribute="date_created", dump_only=True)
    config = HookConfigField()

    @post_load(pass_many=False)
    def make_hook(self, data, **kwargs):
        if self.context.get("hook"):
            hook = self.context["hook"]
            for key, value in data.items():
                setattr(hook, key, value)
        else:
            hook = Hook(**data)
        return hook

    def get_token(self, obj):
        # we allow visibility of tokens for 24 hours
        if obj.date_created > timezone.now() - timedelta(days=1):
            return urlsafe_b64encode(obj.token).decode("utf-8")

        return None

    def get_public_uri(self, obj):
        return "/hooks/{}/public".format(str(obj.id))

    def get_secret_uri(self, obj):
        return "/hooks/{}/{}".format(str(obj.id), obj.get_signature())

    def get_provider_name(self, obj):
        provider_cls = get_provider(obj.provider)
        return provider_cls.get_name(obj.config or {})
