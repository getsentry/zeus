from factory import alchemy

from zeus.config import db


class ModelFactory(alchemy.SQLAlchemyModelFactory):
    """
    Similar to the built-in SQLAlchemy factory, except it uses
    our dynamic session.
    """

    class Meta:
        abstract = True
        sqlalchemy_session = None
        sqlalchemy_session_persistence = None
        force_flush = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Create an instance of the model, and save it to the database.
        """
        session = getattr(cls._meta, "sqlalchemy_session", None) or db.session
        session_persistence = cls._meta.sqlalchemy_session_persistence
        if cls._meta.force_flush:
            session_persistence = alchemy.SESSION_PERSISTENCE_FLUSH

        obj = model_class(*args, **kwargs)
        session.add(obj)
        if session_persistence == alchemy.SESSION_PERSISTENCE_FLUSH:
            session.flush()
        elif session_persistence == alchemy.SESSION_PERSISTENCE_COMMIT:
            session.commit()
        return obj
