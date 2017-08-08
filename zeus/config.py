import logging

from flask import Flask
from flask_alembic import Alembic
from flask_sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry

from zeus.utils.celery import Celery
from zeus.utils.redis import Redis

import os

ROOT = os.path.join(os.path.dirname(__file__), os.pardir)

alembic = Alembic()
celery = Celery()
db = SQLAlchemy()
redis = Redis()
sentry = Sentry(logging=True, level=logging.WARN)


def create_app(_read_config=True, **config):
    app = Flask(
        __name__,
        static_folder=os.path.join(ROOT, 'static'),
        template_folder=os.path.join(ROOT, 'templates'),
    )

    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'SQLALCHEMY_DATABASE_URI', 'postgresql:///zeus'
    )
    app.config['SQLALCHEMY_POOL_SIZE'] = 60
    app.config['SQLALCHEMY_MAX_OVERFLOW'] = 20
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # support for kubernetes
    # https://kubernetes.io/docs/concepts/services-networking/service/
    if os.environ.get('GET_HOSTS_FROM') == 'env':
        REDIS_URL = 'redis://{}:{}/0'.format(
            os.environ['REDIS_MASTER_SERVICE_HOST'],
            os.environ['REDIS_MASTER_SERVICE_PORT'],
        )
    else:
        REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost/0')

    app.config['REDIS_URL'] = REDIS_URL

    app.config['SENTRY_DSN'] = os.environ.get('SENTRY_DSN') or None
    app.config['SENTRY_INCLUDE_PATHS'] = [
        'changes',
    ]

    app.config['GITHUB_CLIENT_ID'] = os.environ.get('GITHUB_CLIENT_ID') or None
    app.config['GITHUB_CLIENT_SECRET'] = os.environ.get('GITHUB_CLIENT_SECRET') or None

    app.config['CELERY_ACCEPT_CONTENT'] = ['zeus_json', 'json']
    app.config['CELERY_ACKS_LATE'] = True
    app.config['CELERY_BROKER_URL'] = app.config['REDIS_URL']
    app.config['CELERY_DEFAULT_QUEUE'] = 'default'
    app.config['CELERY_DEFAULT_EXCHANGE'] = 'default'
    app.config['CELERY_DEFAULT_EXCHANGE_TYPE'] = 'direct'
    app.config['CELERY_DEFAULT_ROUTING_KEY'] = 'default'
    app.config['CELERY_DISABLE_RATE_LIMITS'] = True
    app.config['CELERY_EVENT_SERIALIZER'] = 'zeus_json'
    app.config['CELERY_IGNORE_RESULT'] = True
    app.config['CELERY_IMPORTS'] = ('zeus.tasks', )
    app.config['CELERY_RESULT_BACKEND'] = None
    app.config['CELERY_RESULT_SERIALIZER'] = 'zeus_json'
    app.config['CELERY_SEND_EVENTS'] = False
    app.config['CELERY_TASK_RESULT_EXPIRES'] = 1
    app.config['CELERY_TASK_SERIALIZER'] = 'zeus_json'
    app.config['CELERYD_PREFETCH_MULTIPLIER'] = 1
    app.config['CELERYD_MAX_TASKS_PER_CHILD'] = 10000

    app.config['REPO_ROOT'] = os.environ.get('REPO_ROOT', '/usr/local/cache/zeus-repos')

    # app.config['DEFAULT_FILE_STORAGE'] = ''

    if _read_config:
        if os.environ.get('ZEUS_CONF'):
            # ZEUS_CONF=/etc/zeus.conf.py
            app.config.from_envvar('ZEUS_CONF')
        else:
            # Look for ~/.zeus/zeus.conf.py
            path = os.path.normpath(os.path.expanduser('~/.zeus/zeus.config.py'))
            app.config.from_pyfile(path, silent=True)

    app.config.update(config)

    from zeus.testutils.client import ZeusTestClient
    app.test_client_class = ZeusTestClient

    # init sentry first
    sentry.init_app(app)

    configure_db(app)

    redis.init_app(app)

    celery.init_app(app, sentry)

    configure_api(app)
    configure_web(app)

    from . import models  # NOQA

    return app


def configure_db(app):
    from sqlalchemy import event
    from sqlalchemy.orm import mapper
    from sqlalchemy.inspection import inspect

    alembic.init_app(app)
    db.init_app(app)

    @event.listens_for(mapper, "init")
    def instant_defaults_listener(target, args, kwargs):
        for key, column in inspect(type(target)).columns.items():
            if column.default is not None:
                if callable(column.default.arg):
                    setattr(target, key, column.default.arg(target))
                else:
                    setattr(target, key, column.default.arg)

    event.listen(mapper, 'init', instant_defaults_listener)


def configure_api(app):
    from zeus import api

    app.register_blueprint(api.app, url_prefix='/api')


def configure_web(app):
    from zeus import web

    app.register_blueprint(web.app, url_prefix='')
