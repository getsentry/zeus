from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.sql.expression import literal_column

from zeus.config import db


def try_create(model, where: dict, defaults: dict = None) -> bool:
    stmt = (
        pg_insert(model)
        .values(**where, **defaults or {})
        .on_conflict_do_nothing(index_elements=list(where.keys()))
    )
    with db.session.begin_nested():
        rv = db.session.execute(stmt)
    return bool(rv.rowcount)


def try_update(model, where: dict, values: dict) -> bool:
    result = (
        db.session.query(type(model))
        .filter_by(**where)
        .update(values, synchronize_session=False)
    )
    return result.rowcount > 0


def get_or_create(model, where: dict, defaults: dict = None):
    created = False

    instance = model.query.filter_by(**where).first()
    if instance is not None:
        return instance, created

    created = try_create(model, where, defaults)
    instance = model.query.filter_by(**where).first()
    if instance is None:
        # this should never happen unless everything is broken
        raise Exception("Unable to get or create instance")

    return instance, created


def create_or_update(model, where: dict, values: dict = None):
    stmt = (
        pg_insert(model)
        .values(**where, **values or {})
        .on_conflict_do_update(index_elements=list(where.keys()), set_=values or where)
        .returning(
            literal_column(
                "case when xmax::text::int > 0 then 'updated' else 'inserted' end"
            )
        )
    )
    with db.session.begin_nested():
        rv = db.session.execute(stmt)
    return rv.fetchone()[0] == "inserted"


def create_or_get(model, where: dict, values: dict = None):
    if values is None:
        values = {}

    created = False

    instance = model.query.filter_by(**where).first()
    if instance is None:
        created = try_create(model, where, values)
        instance = model.query.filter_by(**where).first()
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
