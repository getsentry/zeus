from __future__ import absolute_import, print_function

from .manager import Manager
from .checkstyle import CheckstyleHandler
from .coverage import CoverageHandler
from .gotest import GoTestHandler
from .pycodestyle import PyCodeStyleHandler
from .pylint import PyLintHandler
from .webpack import WebpackStatsHandler
from .xunit import XunitHandler

manager = Manager()
manager.register(CheckstyleHandler, ["checkstyle.xml", "*.checkstyle.xml"])
manager.register(CoverageHandler, ["coverage.xml", "*.coverage.xml"])
manager.register(GoTestHandler, ["gotest.json", "*.gotest.json"])
manager.register(
    PyCodeStyleHandler,
    [
        "pep8.txt",
        "*.pep8.txt",
        "pep8.log",
        "*.pep8.log",
        "pycodestyle.txt",
        "*.pycodestyle.txt",
        "pycodestyle.log",
        "*.pycodestyle.log",
    ],
)
manager.register(
    PyLintHandler, ["pylint.txt", "*.pylint.txt", "pylint.log", "*.pylint.log"]
)
manager.register(WebpackStatsHandler, ["compilation-stats.json"])
manager.register(XunitHandler, ["xunit.xml", "junit.xml", "*.xunit.xml", "*.junit.xml"])
