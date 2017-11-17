from zeus.constants import Severity

from .enum import EnumField


class SeverityField(EnumField):
    enum = Severity
