import celery
import json

from kombu import serialization
from kombu.utils.encoding import bytes_t
from raven.contrib.celery import register_signal, register_logger_signal
from uuid import UUID


class Celery(object):
    def __init__(self, app=None, sentry=None):
        self.celery = None
        if app:
            self.init_app(app, sentry)
        register_serializer()

    def init_app(self, app, sentry):
        class ContextTask(celery.Task):
            abstract = True

            # TODO(dcramer): I THINK we dont need app_context when we're already within context,
            # but its 100% causing issues with sqlalchemy sessions and relationships if you
            # are calling a task inline (vs .delay)
            def __call__(self, *args, **kwargs):
                _app_context = kwargs.pop('_app_context', True)
                if not _app_context:
                    return super(ContextTask, self).__call__(*args, **kwargs)
                with app.app_context():
                    return super(ContextTask, self).__call__(*args, **kwargs)

        self.celery = celery.Celery(
            app.import_name,
            backend=app.config['CELERY_RESULT_BACKEND'],
            broker=app.config['CELERY_BROKER_URL'],
            task_cls=ContextTask
        )
        self.celery.conf.update(app.config)

        if sentry:
            register_signal(sentry.client)
            register_logger_signal(sentry.client)

    def get_celery_app(self):
        return self.celery


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, value):
        if isinstance(value, UUID):
            return str(value)
        elif isinstance(value, bytes_t):
            return value.decode()
        return value


def register_serializer():
    serialization.register(
        'zeus_json',
        lambda v: json.dumps(v, cls=EnhancedJSONEncoder),
        json.loads,
        content_type='application/json',
        content_encoding='utf-8'
    )
