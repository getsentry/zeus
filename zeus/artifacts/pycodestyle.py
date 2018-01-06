import re

from zeus.config import db
from zeus.constants import Severity
from zeus.models import StyleViolation

from .base import ArtifactHandler

regexp = re.compile(
    r'^(?P<filename>[^\:]+)\:(?P<lineno>\d+)\:(?P<colno>\d+)\: (?P<source>[a-z]\d+) (?P<message>.+)$', re.I)

SEVERITY_MAP = {
    'W': Severity.warning,
    'E': Severity.error,
    'F': Severity.error,
}


class PyCodeStyleHandler(ArtifactHandler):
    supported_types = frozenset(
        ['text/x-pep8', 'text/x-pycodestyle', 'text/plain+pep8', 'text/plain+pycodestyle'])

    def process(self, fp):
        job = self.job
        for line in fp:
            # optparse.py:69:11: E401 multiple imports on one line
            parsed = regexp.match(line.decode('utf-8'))
            if not parsed:
                continue

            severity = SEVERITY_MAP.get(
                parsed.group('source')[0], Severity.info)

            db.session.add(StyleViolation(
                job=job,
                repository_id=job.repository_id,
                filename=parsed.group('filename'),
                severity=severity,
                message=parsed.group('message'),
                source=parsed.group('source'),
                lineno=parsed.group('lineno'),
                colno=parsed.group('colno'),
            ))
        db.session.flush()
