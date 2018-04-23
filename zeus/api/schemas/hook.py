import jsonschema

from base64 import urlsafe_b64encode
from datetime import timedelta
from marshmallow import Schema, fields, post_load
from marshmallow.exceptions import ValidationError

from zeus.models import Hook
from zeus.utils import timezone

from zeus.providers.custom import CustomProvider
from zeus.providers.travis import TravisProvider


ALIASES = {"travis-ci": "travis"}

PROVIDERS = {"travis": TravisProvider, "custom": CustomProvider}


class HookConfigField(fields.Field):

    def _serialize(self, value, attr, obj):
        return dict(value) if value else {}

    def _deserialize(self, value, attr, data):
        provider_name = data.get("provider")
        if provider_name:
            try:
                provider_cls = PROVIDERS[ALIASES.get(provider_name, provider_name)]()
            except KeyError:
                raise ValidationError("Invalid provider")

            try:
                provider_cls.validate_config(value)
            except jsonschema.ValidationError as e:
                raise ValidationError from e

        return value


class HookSchema(Schema):
    id = fields.UUID(dump_only=True)
    provider = fields.Str(
        validate=[
            fields.validate.OneOf(
                choices=list(set(PROVIDERS.keys()).union(ALIASES.keys()))
            )
        ]
    )
    token = fields.Method("get_token", dump_only=True)
    secret_uri = fields.Method("get_secret_uri", dump_only=True)
    public_uri = fields.Method("get_public_uri", dump_only=True)
    created_at = fields.DateTime(attribute="date_created", dump_only=True)
    config = HookConfigField()

    @post_load
    def make_hook(self, data):
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
