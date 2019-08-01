import json
import logging
import os
import sys
import tempfile

from datetime import timedelta
from flask import Flask
from flask_alembic import Alembic
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

from zeus.utils.celery import Celery
from zeus.utils.metrics import Metrics
from zeus.utils.nplusone import NPlusOne
from zeus.utils.redis import Redis
from zeus.utils.ssl import SSL

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

WORKSPACE_ROOT = os.path.expanduser(os.environ.get("WORKSPACE_ROOT", "~/.zeus/"))

# Sigh. If only developers would stop having feelings, and use more facts.
# HTTP (non-SSL) is a valid callback URL for many OAuth2 providers, especially
# when you're running on localhost.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

alembic = Alembic()
celery = Celery()
db = SQLAlchemy()
mail = Mail()
nplusone = NPlusOne()
redis = Redis()
ssl = SSL()
metrics = Metrics()


def with_health_check(app):
    def middleware(environ, start_response):
        if environ.get("PATH_INFO", "") == "/healthz":
            start_response("200 OK", [("Content-Type", "application/json")])
            return [b'{"ok": true}']

        return app(environ, start_response)

    return middleware


def create_app(_read_config=True, **config):
    app = Flask(
        __name__,
        static_folder=os.path.join(ROOT, "static"),
        template_folder=os.path.join(ROOT, "templates"),
    )

    # support for kubernetes
    # https://kubernetes.io/docs/concepts/services-networking/service/
    if os.environ.get("GET_HOSTS_FROM") == "env":
        REDIS_URL = "redis://{}:{}/0".format(
            os.environ["REDIS_MASTER_SERVICE_HOST"],
            os.environ["REDIS_MASTER_SERVICE_PORT"],
        )
        # Cloud SQL
        # https://cloud.google.com/sql/docs/postgres/connect-container-engine
        SQLALCHEMY_URI = "postgresql+psycopg2://{}:{}@127.0.0.1:5432/zeus".format(
            os.environ["DB_USER"], os.environ["DB_PASSWORD"]
        )
        if "CELERY_BROKER_URL" in os.environ:
            app.config["CELERY_BROKER_URL"] = os.environ["CELERY_BROKER_URL"]

        if "GCS_BUCKET" in os.environ:
            app.config["FILE_STORAGE"] = {
                "backend": "zeus.storage.gcs.GoogleCloudStorage",
                "options": {
                    "bucket": os.environ["GCS_BUCKET"],
                    "project": os.environ.get("GC_PROJECT"),
                },
            }
        app.config.setdefault("MAIL_SERVER", os.environ.get("MAIL_SERVER"))
        app.config.setdefault("MAIL_PORT", os.environ.get("MAIL_PORT"))
        app.config.setdefault(
            "MAIL_USE_TLS", bool(int(os.environ.get("MAIL_USE_TLS", "1")))
        )
        app.config.setdefault(
            "MAIL_USE_SSL", bool(int(os.environ.get("MAIL_USE_SSL", "0")))
        )
        app.config.setdefault("MAIL_USERNAME", os.environ.get("MAIL_USERNAME"))
        app.config.setdefault("MAIL_PASSWORD", os.environ.get("MAIL_PASSWORD"))
        app.config.setdefault(
            "MAIL_DEFAULT_SENDER", os.environ.get("MAIL_DEFAULT_SENDER")
        )
        app.config.setdefault(
            "ALLOWED_ORIGINS",
            [
                x.strip()
                for x in os.environ.get("ALLOWED_ORIGINS", "").split(",")
                if x.strip()
            ],
        )
    else:
        REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1/0")
        SQLALCHEMY_URI = os.environ.get(
            "SQLALCHEMY_DATABASE_URI", "postgresql+psycopg2://postgres@127.0.0.1/zeus"
        )
        app.config["FILE_STORAGE"] = {
            "backend": "zeus.storage.base.FileStorage",
            "options": {},
        }
        app.config["CELERY_BROKER_URL"] = REDIS_URL

    app.config.setdefault(
        "MAIL_DEFAULT_SENDER", "{}@localhost".format(os.environ.get("USERNAME", "root"))
    )

    if os.environ.get("SERVER_NAME"):
        app.config["SERVER_NAME"] = os.environ["SERVER_NAME"]

    app.config.setdefault(
        "DOMAIN",
        app.config.get("SERVER_NAME") or os.environ.get("DOMAIN") or "localhost",
    )

    app.config["PUBSUB_ENDPOINT"] = os.environ.get(
        "PUBSUB_ENDPOINT", "http://localhost:8090"
    )

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

    app.config["LOG_LEVEL"] = os.environ.get("LOG_LEVEL") or "INFO"

    app.config["SSL"] = os.environ.get("SSL") in ("1", "true", "on")

    # limit sessions to one day so permissions are revalidated automatically
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=1)

    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["MOCK_REVISIONS"] = bool(os.environ.get("MOCK_REVISIONS"))

    app.config["REDIS_URL"] = REDIS_URL

    app.config["SENTRY_DSN_FRONTEND"] = os.environ.get("SENTRY_DSN_FRONTEND") or None
    app.config["GITHUB_CLIENT_ID"] = os.environ.get("GITHUB_CLIENT_ID") or None
    app.config["GITHUB_CLIENT_SECRET"] = os.environ.get("GITHUB_CLIENT_SECRET") or None

    app.config["WEBPACK_MANIFEST_PATH"] = os.path.join(
        ROOT, "static", "asset-manifest.json"
    )

    app.config["CELERY_ACCEPT_CONTENT"] = ["zeus_json", "json"]
    app.config["CELERY_ACKS_LATE"] = True
    app.config.setdefault("CELERY_BROKER_URL", app.config["REDIS_URL"])
    app.config["CELERY_DEFAULT_QUEUE"] = "default"
    app.config["CELERY_DEFAULT_EXCHANGE"] = "default"
    app.config["CELERY_DEFAULT_EXCHANGE_TYPE"] = "direct"
    app.config["CELERY_DEFAULT_ROUTING_KEY"] = "default"
    app.config["CELERY_DISABLE_RATE_LIMITS"] = True
    app.config["CELERY_EVENT_SERIALIZER"] = "zeus_json"
    app.config["CELERY_IGNORE_RESULT"] = True
    app.config["CELERY_IMPORTS"] = ("zeus.tasks",)
    app.config["CELERY_RESULT_BACKEND"] = None
    app.config["CELERY_RESULT_SERIALIZER"] = "zeus_json"
    # app.config['CELERY_SEND_EVENTS'] = False
    app.config["CELERY_TASK_RESULT_EXPIRES"] = 1
    app.config["CELERY_TASK_SERIALIZER"] = "zeus_json"
    # dont let any task run longer than 5 minutes
    app.config["CELERY_TASK_SOFT_TIME_LIMIT"] = 300
    # hard kill tasks after 6 minutes
    app.config["CELERY_TASK_TIME_LIMIT"] = 360
    # app.config['CELERYD_PREFETCH_MULTIPLIER'] = 1
    # app.config['CELERYD_MAX_TASKS_PER_CHILD'] = 10000
    app.config["CELERYBEAT_SCHEDULE_FILE"] = os.path.join(
        tempfile.gettempdir(), "zeus-celerybeat"
    )
    app.config["CELERYBEAT_SCHEDULE"] = {
        "sync-all-repos": {
            "task": "zeus.sync_all_repos",
            "schedule": timedelta(minutes=5),
        },
        "cleanup-builds": {
            "task": "zeus.cleanup_builds",
            "schedule": timedelta(minutes=5),
        },
        "cleanup-artifacts": {
            "task": "zeus.cleanup_artifacts",
            "schedule": timedelta(minutes=60),
        },
    }
    app.config["REDBEAT_REDIS_URL"] = app.config["REDIS_URL"]

    app.config["WORKSPACE_ROOT"] = WORKSPACE_ROOT
    app.config["REPO_ROOT"] = os.environ.get(
        "REPO_ROOT", os.path.join(WORKSPACE_ROOT, "zeus-repos")
    )
    app.config["REPO_SYNC_INTERVAL"] = timedelta(minutes=60)

    app.config["ARTIFACT_RETENTION"] = timedelta(days=30)

    if _read_config:
        if os.environ.get("ZEUS_CONF"):
            # ZEUS_CONF=/etc/zeus.conf.py
            app.config.from_envvar("ZEUS_CONF")
        else:
            # Look for $WORKSPACE_ROOT/zeus.conf.py
            app.config.from_pyfile(
                os.path.join(WORKSPACE_ROOT, "zeus.config.py"), silent=True
            )

    app.wsgi_app = with_health_check(app.wsgi_app)

    app.config.update(config)

    app.config.setdefault("MAIL_SUPPRESS_SEND", app.debug or app.testing)

    # HACK(dcramer): the CLI causes validation to happen on init, which it shouldn't
    if "init" not in sys.argv:
        req_vars = (
            "GITHUB_CLIENT_ID",
            "GITHUB_CLIENT_SECRET",
            "REDIS_URL",
            "SECRET_KEY",
            "SQLALCHEMY_DATABASE_URI",
        )
        for varname in req_vars:
            if not app.config.get(varname):
                raise SystemExit(
                    "Required configuration not present for {}".format(varname)
                )

    from zeus.testutils.client import ZeusTestClient

    app.test_client_class = ZeusTestClient

    if app.config.get("LOG_LEVEL"):
        app.logger.setLevel(getattr(logging, app.config["LOG_LEVEL"].upper()))

    # oauthlib compat
    app.config["GITHUB_CONSUMER_KEY"] = app.config["GITHUB_CLIENT_ID"]
    app.config["GITHUB_CONSUMER_SECRET"] = app.config["GITHUB_CLIENT_SECRET"]

    if app.config["SSL"]:
        ssl.init_app(app)

    metrics.init_app(app)

    configure_db(app)

    redis.init_app(app)
    mail.init_app(app)
    celery.init_app(app)

    configure_webpack(app)
    configure_sentry(app)

    configure_api(app)
    configure_web(app)

    @app.after_request
    def track_user(response):
        from zeus import auth
        from zeus.utils import timezone

        user = auth.get_current_user(fetch=False)
        if user and user.date_active < timezone.now() - timedelta(minutes=5):
            user.date_active = timezone.now()
            db.session.add(user)
            db.session.commit()
        return response

    from . import models  # NOQA

    return app


def configure_db(app):
    from sqlalchemy import event
    from sqlalchemy.orm import mapper
    from sqlalchemy.inspection import inspect

    alembic.init_app(app)
    db.init_app(app)
    nplusone.init_app(app)

    @event.listens_for(mapper, "init")
    def instant_defaults_listener(target, args, kwargs):
        for key, column in inspect(type(target)).columns.items():
            if column.default is not None:
                if callable(column.default.arg):
                    setattr(target, key, column.default.arg(target))
                else:
                    setattr(target, key, column.default.arg)

    event.listen(mapper, "init", instant_defaults_listener)


def configure_api(app):
    from zeus import api

    app.register_blueprint(api.app, url_prefix="/api")


def configure_web(app):
    from zeus import web

    app.register_blueprint(web.app, url_prefix="")

    if app.debug:
        from zeus.web import debug

        app.register_blueprint(debug.app, url_prefix="/debug")


def configure_webpack(app):
    from flask import url_for

    app.extensions["webpack"] = {"assets": None}

    def get_asset(path):
        assets = app.extensions["webpack"]["assets"]
        # in debug we read in this file each request
        if assets is None or app.debug:
            try:
                with open(app.config["WEBPACK_MANIFEST_PATH"]) as fp:
                    assets = json.load(fp)
            except FileNotFoundError:
                app.logger.exception("Unable to load webpack manifest")
                assets = {}
            app.extensions["webpack"]["assets"] = assets
        return url_for("static", filename=assets.get(path, path))

    @app.context_processor
    def webpack_assets():
        return {"asset_url": get_asset}


def configure_sentry(app):
    from sentry_sdk import init
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.flask import FlaskIntegration

    release = os.environ.get("BUILD_REVISION") or None
    if not release:
        try:
            import subprocess

            release = str(
                subprocess.check_output(["git", "describe", "--always"])
            ).strip()
        except Exception:
            app.logger.warn("Unable to get release from git", exc_info=True)

    # set into env for compatibility with existing code
    app.config["SENTRY_RELEASE"] = release
    app.config["SENTRY_ENVIRONMENT"] = environment = (
        os.environ.get("NODE_ENV", "development") or None
    )

    init(
        integrations=[FlaskIntegration(transaction_style="url"), CeleryIntegration()],
        in_app_include=["zeus"],
        release=release,
        environment=environment,
    )
