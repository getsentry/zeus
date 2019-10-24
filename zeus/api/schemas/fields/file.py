from marshmallow import fields


class FileField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None

        elif isinstance(value, dict):
            return value

        return {"name": value.filename, "size": value.size}

    def _deserialize(self, value, attr, data, **kwargs):
        # XXX(dcramer): this would need to serialize into something compatible with
        # the schema
        return None
