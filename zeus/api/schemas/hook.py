from base64 import urlsafe_b64encode
from datetime import timedelta
from marshmallow import Schema, fields, post_load

from zeus.models import Hook
from zeus.utils import timezone


class HookSchema(Schema):
    id = fields.UUID(dump_only=True)
    provider = fields.Str()
    token = fields.Method('get_token', dump_only=True)
    base_uri = fields.Method('get_base_uri', dump_only=True)
    created_at = fields.DateTime(attribute="date_created", dump_only=True)

    @post_load
    def make_hook(self, data):
        return Hook(**data)

    def get_token(self, obj):
        # we allow visibility of tokens for 24 hours
        if obj.date_created > timezone.now() - timedelta(days=1):
            return urlsafe_b64encode(obj.token).decode('utf-8')
        return None

    def get_base_uri(self, obj):
        return '/hooks/{}/{}'.format(str(obj.id), obj.get_signature())
