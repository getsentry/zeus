from collections import defaultdict
from marshmallow import Schema, fields, pre_dump, validate


class MailOptionsSchema(Schema):
    notify_author = fields.String(value=validate.ContainsOnly(["1", "0"]), missing="1")


class UserOptionsSchema(Schema):
    mail = fields.Nested(MailOptionsSchema)

    @pre_dump
    def process_options(self, data, **kwargs):
        result = defaultdict(lambda: defaultdict(int))
        result["mail"]["notify_author"] = "1"
        for option in data:
            bits = option.name.split(".", 1)
            if len(bits) != 2:
                continue

            result[bits[0]][bits[1]] = option.value
        return result


class UserSchema(Schema):
    id = fields.UUID(dump_only=True)
    email = fields.Str(dump_only=True)
    options = fields.Nested(UserOptionsSchema)
    created_at = fields.DateTime(attribute="date_created", dump_only=True)
