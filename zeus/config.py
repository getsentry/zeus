import logging
import raven

from datetime import timedelta
from flask import Flask
from flask_alembic import Alembic
from flask_sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry

from zeus.utils.celery import Celery
from zeus.utils.redis import Redis

import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

alembic = Alembic()
celery = Celery()
db = SQLAlchemy()
redis = Redis()
sentry = Sentry(logging=True, level=logging.WARN, wrap_wsgi=True)


def force_ssl(app):
    def middleware(environ, start_response):
        environ['wsgi.url_scheme'] = 'https'
        return app(environ, start_response)

    return middleware


def create_app(_read_config=True, **config):
    app = Flask(
        __name__,
        static_folder=os.path.join(ROOT, 'static'),
        template_folder=os.path.join(ROOT, 'templates'),
    )

    # support for kubernetes
    # https://kubernetes.io/docs/concepts/services-networking/service/
    if os.environ.get('GET_HOSTS_FROM') == 'env':
        REDIS_URL = 'redis://{}:{}/0'.format(
            os.environ['REDIS_MASTER_SERVICE_HOST'],
            os.environ['REDIS_MASTER_SERVICE_PORT'],
        )
        # Cloud SQL
        # https://cloud.google.com/sql/docs/postgres/connect-container-engine
        SQLALCHEMY_URI = 'postgresql+psycopg2://{}:{}@127.0.0.1:5432/zeus'.format(
            os.environ['DB_USER'],
            os.environ['DB_PASSWORD'],
        )
        if 'GCS_BUCKET' in os.environ:
            app.config['FILE_STORAGE'] = {
                'backend': 'zeus.storage.gcs.GoogleCloudStorage',
                'options': {
                    'bucket': os.environ['GCS_BUCKET'],
                    'project': os.environ.get('GC_PROJECT'),
                },
            }
    else:
        REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost/0')
        SQLALCHEMY_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'postgresql+psycopg2:///zeus')
        app.config['FILE_STORAGE'] = {
            'backend': 'zeus.storage.base.FileStorage',
            'options': {},
        }

    if os.environ.get('SERVER_NAME'):
        app.config['SERVER_NAME'] = os.environ['SERVER_NAME']

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

    app.config['LOG_LEVEL'] = os.environ.get('LOG_LEVEL') or 'INFO'

    app.config['SSL'] = os.environ.get('SSL') in ('1', 'true', 'on')

    # limit sessions to one day so permissions are revalidated automatically
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['REDIS_URL'] = REDIS_URL

    app.config['SENTRY_DSN'] = os.environ.get('SENTRY_DSN') or None
    app.config['SENTRY_DSN_FRONTEND'] = os.environ.get('SENTRY_DSN_FRONTEND') or None
    app.config['SENTRY_INCLUDE_PATHS'] = [
        'zeus',
    ]
    try:
        app.config['SENTRY_RELEASE'] = raven.fetch_git_sha(ROOT)
    except Exception:
        app.logger.warn('unable to bind sentry.release context', exc_info=True)
    app.config['SENTRY_ENVIRONMENT'] = os.environ.get('NODE_ENV', 'development')

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

    if _read_config:
        if os.environ.get('ZEUS_CONF'):
            # ZEUS_CONF=/etc/zeus.conf.py
            app.config.from_envvar('ZEUS_CONF')
        else:
            # Look for ~/.zeus/zeus.conf.py
            path = os.path.normpath(os.path.expanduser('~/.zeus/zeus.config.py'))
            app.config.from_pyfile(path, silent=True)

    app.config.update(config)

    req_vars = (
        'GITHUB_CLIENT_ID', 'GITHUB_CLIENT_SECRET', 'REDIS_URL', 'SECRET_KEY',
        'SQLALCHEMY_DATABASE_URI'
    )
    for varname in req_vars:
        if not app.config.get(varname):
            raise SystemExit('Required configuration not present for {}'.format(varname))

    if app.config.get('SSL'):
        app.wgsi_app = force_ssl(app)
        app.config['PREFERRED_URL_SCHEME'] = 'https'
        app.config['SESSION_COOKIE_SECURE'] = True

    from zeus.testutils.client import ZeusTestClient
    app.test_client_class = ZeusTestClient

    if app.config.get('LOG_LEVEL'):
        app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL'].upper()))

    # init sentry first
    sentry.init_app(app)
    # XXX(dcramer): Sentry + Flask + Logging integration is broken
    # https://github.com/getsentry/raven-python/issues/1030
    from raven.handlers.logging import SentryHandler
    app.logger.addHandler(SentryHandler(client=sentry.client, level=logging.WARN))

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
