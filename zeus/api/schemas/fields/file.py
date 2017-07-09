from marshmallow import fields


class FileField(fields.Field):
    def _serialize(self, value, attr, obj):
        if value is None:
            return None
        return {'name': value.filename}

    def _deserialize(value, attr, data):
        if value is None:
            return None
        return value
