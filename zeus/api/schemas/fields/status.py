from zeus.constants import Status

from .enum import EnumField


class StatusField(EnumField):
    enum = Status
