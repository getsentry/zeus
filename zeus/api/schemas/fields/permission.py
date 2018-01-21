from zeus.constants import Permission

from .enum import EnumField


class PermissionField(EnumField):
    enum = Permission
