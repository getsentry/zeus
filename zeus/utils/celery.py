import celery


class Celery(object):
    def __init__(self, app=None):
        self.celery = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.celery = celery.Celery(
            app.import_name,
            backend=app.config['CELERY_RESULT_BACKEND'],
            broker=app.config['CELERY_BROKER_URL']
        )
        self.celery.conf.update(app.config)

        class ContextTask(self.celery.Task):
            abstract = True

            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return super(ContextTask, self).__call__(*args, **kwargs)
        self.celery.Task = ContextTask
        self.register_json_serializer()

    def get_celery_app(self):
        return self.celery

    def register_json_serializer(self):
        from kombu.serialization import register
        from kombu.utils.encoding import bytes_t
        from json import dumps, loads
        from uuid import UUID

        def _loads(obj):
            if isinstance(obj, UUID):
                obj = obj.hex
            elif isinstance(obj, bytes_t):
                obj = obj.decode()
            return loads(obj)

        register('zeus_json', dumps, _loads,
                 content_type='application/json',
                 content_encoding='utf-8')

    @property
    def task(self, *args, **kwargs):
        return self.celery.task(*args, **kwargs)
