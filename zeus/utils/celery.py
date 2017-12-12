import celery
import json

from kombu import serialization
from kombu.utils.encoding import bytes_t
from raven.contrib.celery import register_signal, register_logger_signal
from uuid import UUID


class Celery(object):
    def __init__(self, app=None, sentry=None):
        # we create the celery immediately as otherwise NOTHING WORKS
        self.app = None
        self.context = None
        self.celery = celery.Celery(__name__)

        TaskBase = self.celery.Task

        class ContextualTask(TaskBase):
            def __call__(self, *args, **kwargs):
                with self.flask_app.app_context():
                    return TaskBase.__call__(self, *args, **kwargs)

        self.celery.Task = ContextualTask

        if app:
            self.init_app(app, sentry)
        register_serializer()

    def init_app(self, app, sentry):
        self.app = app
        new_celery = celery.Celery(
            app.import_name,
            broker=app.config['CELERY_BROKER_URL'],
            backend=app.config['CELERY_RESULT_BACKEND'],
        )
        # XXX(dcramer): why the hell am I wasting time trying to make Celery work?
        self.celery.__dict__.update(vars(new_celery))
        self.celery.conf.update(app.config)
        self.celery.flask_app = app

        if sentry:
            register_signal(sentry.client)
            register_logger_signal(sentry.client)

    def task(self, *args, **kwargs):
        return self.celery.task(*args, **kwargs)

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
