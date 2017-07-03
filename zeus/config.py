import logging

from flask import Flask
from flask_alembic import Alembic
from flask_sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry

import os

ROOT = os.path.join(os.path.dirname(__file__), os.pardir)

alembic = Alembic()
db = SQLAlchemy()
sentry = Sentry(logging=True, level=logging.WARN)


def create_app(_read_config=True, **config):
    app = Flask(
        __name__,
        static_folder=os.path.join(ROOT, 'static'),
        template_folder=os.path.join(ROOT, 'templates'),
    )

    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///zeus'
    app.config['SQLALCHEMY_POOL_SIZE'] = 60
    app.config['SQLALCHEMY_MAX_OVERFLOW'] = 20
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['SENTRY_DSN'] = None
    app.config['SENTRY_INCLUDE_PATHS'] = [
        'changes',
    ]

    app.config['GITHUB_CLIENT_ID'] = None
    app.config['GITHUB_CLIENT_SECRET'] = None

    # app.config['DEFAULT_FILE_STORAGE'] = ''

    if _read_config:
        if os.environ.get('ZEUS_CONF'):
            # ZEUS_CONF=/etc/zeus.conf.py
            app.config.from_envvar('ZEUS_CONF')
        else:
            # Look for ~/.zeus/zeus.conf.py
            path = os.path.normpath(
                os.path.expanduser('~/.zeus/zeus.config.py'))
            app.config.from_pyfile(path, silent=True)

    app.config.update(config)

    # init sentry first
    sentry.init_app(app)

    alembic.init_app(app)
    db.init_app(app)

    configure_api(app)
    configure_web(app)

    from . import models  # NOQA

    return app


def configure_api(app):
    from zeus import api

    app.register_blueprint(api.app, url_prefix='/api')


def configure_web(app):
    from zeus import web

    app.register_blueprint(web.app, url_prefix='')
