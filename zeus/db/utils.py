from sqlalchemy.exc import IntegrityError
from typing import Any, Optional, Tuple

from zeus.config import db


def try_create(model, where: dict, defaults: dict = None) -> Optional[Any]:
    if defaults is None:
        defaults = {}

    instance = model()
    for key, value in defaults.items():
        setattr(instance, key, value)
    for key, value in where.items():
        setattr(instance, key, value)
    try:
        with db.session.begin_nested():
            db.session.add(instance)
    except IntegrityError as exc:
        if "duplicate" in str(exc):
            return None
        raise
    return instance


def try_update(model, where: dict, values: dict) -> bool:
    result = (
        db.session.query(type(model))
        .filter_by(**where)
        .update(values, synchronize_session=False)
    )
    return result.rowcount > 0


def get_or_create(model, where: dict, defaults: dict = None) -> Tuple[Any, bool]:
    if defaults is None:
        defaults = {}

    created = False

    instance = model.query.filter_by(**where).first()
    if instance is not None:
        return instance, created

    instance = try_create(model, where, defaults)
    if instance is None:
        instance = model.query.filter_by(**where).first()
    else:
        created = True

    if instance is None:
        # this should never happen unless everything is broken
        raise Exception("Unable to get or create instance")

    return instance, created


def create_or_update(model, where: dict, values: dict = None) -> Tuple[Any, bool]:
    if values is None:
        values = {}

    created = False

    instance = model.query.filter_by(**where).first()
    if instance is None:
        instance = try_create(model, where, values)
        if instance is None:
            instance = model.query.filter_by(**where).first()
            if instance is None:
                raise Exception("Unable to create or update instance")

            update(instance, values)
        else:
            created = True
    else:
        update(instance, values)

    return instance, created


def create_or_get(model, where: dict, values: dict = None) -> Tuple[Any, bool]:
    if values is None:
        values = {}

    created = False

    instance = model.query.filter_by(**where).first()
    if instance is None:
        instance = try_create(model, where, values)
        if instance is None:
            instance = model.query.filter_by(**where).first()
        else:
            created = True

        if instance is None:
            raise Exception("Unable to get or create instance")

    return instance, created


def update(instance, values: dict):
    for key, value in values.items():
        if getattr(instance, key) != value:
            setattr(instance, key, value)
    db.session.add(instance)


def model_repr(*attrs):
    if "id" not in attrs:
        attrs = ("id",) + attrs

    def _repr(self):
        cls = type(self).__name__

        pairs = ("%s=%s" % (a, repr(getattr(self, a, None))) for a in attrs)

        return u"<%s at 0x%x: %s>" % (cls, id(self), ", ".join(pairs))

    return _repr
