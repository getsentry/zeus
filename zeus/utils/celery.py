import celery
import json

from celery.signals import task_postrun, task_prerun, worker_process_init
from kombu import serialization
from kombu.utils.encoding import bytes_t
from uuid import UUID


class Celery(object):
    def __init__(self, app=None):
        # we create the celery immediately as otherwise NOTHING WORKS
        self.app = None
        self.context = None
        self.celery = celery.Celery(__name__)
        if app:
            self.init_app(app)
        register_serializer()

    def init_app(self, app):
        self.app = app
        new_celery = celery.Celery(
            app.import_name,
            broker=app.config["CELERY_BROKER_URL"],
            backend=app.config["CELERY_RESULT_BACKEND"],
        )
        # XXX(dcramer): why the hell am I wasting time trying to make Celery work?
        self.celery.__dict__.update(vars(new_celery))
        self.celery.conf.update(app.config)

        worker_process_init.connect(self._worker_process_init)

        task_postrun.connect(self._task_postrun)
        task_prerun.connect(self._task_prerun)

    def task(self, *args, **kwargs):
        return self.celery.task(*args, **kwargs)

    def get_celery_app(self):
        return self.celery

    def _worker_process_init(self, **kwargs):
        self.app.app_context().push()

    def _task_prerun(self, task, **kwargs):
        if self.app is None:
            return

        context = task._flask_context = [
            self.app.app_context(),
            self.app.test_request_context(),
        ]
        for ctx in context:
            ctx.push()

    def _task_postrun(self, task, **kwargs):
        try:
            context = task._flask_context
        except AttributeError:
            return

        for ctx in context:
            ctx.pop()


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, value):
        if isinstance(value, UUID):
            return str(value)

        elif isinstance(value, bytes_t):
            return value.decode()

        return value


def register_serializer():
    serialization.register(
        "zeus_json",
        lambda v: json.dumps(v, cls=EnhancedJSONEncoder),
        json.loads,
        content_type="application/json",
        content_encoding="utf-8",
    )
