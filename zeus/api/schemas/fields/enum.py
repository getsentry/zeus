from marshmallow.fields import Field
from marshmallow.exceptions import ValidationError


class EnumField(Field):
    enum = None

    def __init__(self, enum=None, *args, **kwargs):
        if enum is not None:
            self.enum = enum
        elif self.enum is None:
            raise ValueError('`enum` must be specified')
        Field.__init__(self, *args, **kwargs)

    def _serialize(self, value, attr, obj):
        if value is None:
            return None
        return value.name

    def _deserialize(self, value, attr, data):
        if value is None:
            return None
        if isinstance(value, self.enum):
            return value
        elif value.startswith('_') or not getattr(self.enum, value):
            raise ValidationError('Not a valid choice.')
        return getattr(self.enum, value)
