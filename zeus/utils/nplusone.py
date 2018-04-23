# -*- coding: utf-8 -*-
import six

from flask import g
from flask import request

import nplusone.ext.sqlalchemy  # noqa

from nplusone.core import signals
from nplusone.core import listeners
from nplusone.core import notifiers


def get_worker():
    try:
        return request._get_current_object()

    except RuntimeError:
        return None


def setup_state():
    signals.get_worker = get_worker


setup_state()


class NPlusOne(object):
    app = None

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def load_config(self):
        self.notifiers = notifiers.init(self.app.config)
        self.whitelist = [
            listeners.Rule(**item)
            for item in self.app.config.get("NPLUSONE_WHITELIST", [])
        ]

    def init_app(self, app):
        self.app = app

        @app.before_request
        def connect():
            self.load_config()
            g.listeners = getattr(g, "listeners", {})
            for name, listener_type in six.iteritems(listeners.listeners):
                g.listeners[name] = listener_type(self)
                g.listeners[name].setup()

        @app.after_request
        def disconnect(response):
            for name, listener_type in six.iteritems(listeners.listeners):
                listener = g.listeners.pop(name, None)
                if listener:
                    listener.teardown()
            return response

    def notify(self, message):
        if not message.match(self.whitelist):
            for notifier in self.notifiers:
                notifier.notify(message)

    def ignore(self, signal):
        return signals.ignore(getattr(signals, signal))
