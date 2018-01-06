from flask import current_app
from lxml import etree

from zeus.config import db
from zeus.constants import Severity
from zeus.models import StyleViolation

from .base import ArtifactHandler


class CheckstyleHandler(ArtifactHandler):
    supported_types = frozenset(
        ['application/x-checkstyle+xml', 'text/xml+checkstyle'])

    def process(self, fp):
        try:
            root = etree.fromstring(fp.read())
        except Exception:
            current_app.logger.exception('Failed to parse XML')
            return []

        job = self.job

        # <file name="/var/lib/jenkins/workspace/Releases/ESLint Release/eslint/fullOfProblems.js">
        #   <error line="1" column="10" severity="error" message="&apos;addOne&apos; is defined but never used. (no-unused-vars)" source="eslint.rules.no-unused-vars" />

        for f_node in root.iter('file'):
            # name
            filename = f_node.get('name')
            for e_node in f_node.iter('error'):
                # line, column, severity, message, source

                db.session.add(StyleViolation(
                    job=job,
                    repository_id=job.repository_id,
                    filename=filename,
                    severity=Severity[e_node.get('severity')],
                    message=e_node.get('message'),
                    source=e_node.get('source'),
                    lineno=e_node.get('line'),
                    colno=e_node.get('column'),
                ))
        db.session.flush()
