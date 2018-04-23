#!/usr/bin/env python

from zeus.utils.imports import import_submodules

import_submodules(locals(), __name__, __path__)


def main():
    import os

    os.environ.setdefault("PYTHONUNBUFFERED", "true")
    os.environ.setdefault("FLASK_APP", "zeus.app")

    from .base import cli

    cli.main()
