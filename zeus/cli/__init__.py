#!/usr/bin/env python

from .auth import *  # NOQA
from .cleanup import *  # NOQA
from .devserver import *  # NOQA
from .hooks import *  # NOQA
from .init import *  # NOQA
from .mocks import *  # NOQA
from .pubsub import *  # NOQA
from .repos import *  # NOQA
from .shell import *  # NOQA
from .ssh_connect import *  # NOQA
from .vcs_server import *  # NOQA
from .web import *  # NOQA
from .worker import *  # NOQA


def main():
    import os

    os.environ.setdefault("PYTHONUNBUFFERED", "true")
    os.environ.setdefault("FLASK_APP", "zeus.app")

    from .base import cli

    cli.main()
