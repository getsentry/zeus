from __future__ import absolute_import, print_function

from .manager import Manager
from .checkstyle import CheckstyleHandler
from .coverage import CoverageHandler
from .xunit import XunitHandler

manager = Manager()
manager.register(CheckstyleHandler, [
                 'checkstyle.xml', '*.checkstyle.xml'])
manager.register(CoverageHandler, [
                 'coverage.xml', '*.coverage.xml'])
manager.register(XunitHandler, [
                 'xunit.xml', 'junit.xml', '*.xunit.xml', '*.junit.xml'])
