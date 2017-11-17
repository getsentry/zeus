from __future__ import absolute_import, print_function

from .manager import Manager
from .checkstyle import CheckstyleHandler
from .coverage import CoverageHandler
from .pycodestyle import PyCodeStyleHandler
from .pylint import PyLintHandler
from .xunit import XunitHandler

manager = Manager()
manager.register(CheckstyleHandler, [
                 'checkstyle.xml', '*.checkstyle.xml'])
manager.register(CoverageHandler, [
                 'coverage.xml', '*.coverage.xml'])
manager.register(XunitHandler, [
                 'xunit.xml', 'junit.xml', '*.xunit.xml', '*.junit.xml'])
manager.register(PyCodeStyleHandler, [
                 'pep8.txt', '*.pep8.txt', 'pycodestyle.txt', '*.pycodestyle.txt'])
manager.register(PyLintHandler, [
                 'pylint.txt', '*.pylint.txt'])
