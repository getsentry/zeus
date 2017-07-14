__all__ = ['Enum', 'IntEnum', 'StrEnum']

from sqlalchemy.types import TypeDecorator, INT, STRINGTYPE


class Enum(TypeDecorator):
    impl = INT

    def __init__(self, enum=None, *args, **kwargs):
        self.enum = enum
        super(Enum, self).__init__(*args, **kwargs)

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return value.value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif self.enum:
            return self.enum(value)
        return value


class IntEnum(Enum):
    pass


class StrEnum(Enum):
    impl = STRINGTYPE
