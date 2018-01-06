import re

from zeus.config import db
from zeus.constants import Severity
from zeus.models import StyleViolation

from .base import ArtifactHandler

regexp = re.compile(
    r'^(?P<filename>.+?)\:(?P<lineno>\d+)\: \[(?P<source>[a-z]\d+)\([^\)]+\), [^\]]*?\] (?P<message>.*)', re.I)

SEVERITY_MAP = {
    'W': Severity.warning,
    'E': Severity.error,
}


class PyLintHandler(ArtifactHandler):
    """
    This supports the output from ``pylint -f parseable``.
    """
    supported_types = frozenset(['text/x-pylint', 'text/plain+pylint'])

    def process(self, fp):
        job = self.job
        for line in fp:
            # zeus/auth.py:20: [C0326(bad - whitespace), ] Exactly one space required around keyword argument assignment
            #     def __init__(self, repository_ids: Optional[str]=None):
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
                # colno=parsed.group('colno'),
            ))
        db.session.flush()
