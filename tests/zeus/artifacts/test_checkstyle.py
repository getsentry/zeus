from io import BytesIO

from zeus.artifacts.checkstyle import CheckstyleHandler
from zeus.constants import Severity
from zeus.models import StyleViolation


def test_result_generation(sample_checkstyle, default_job):
    fp = BytesIO(sample_checkstyle.encode('utf8'))

    handler = CheckstyleHandler(default_job)
    handler.process(fp)

    results = list(StyleViolation.query.unrestricted_unsafe().filter(
        StyleViolation.job_id == default_job.id,
    ).order_by(StyleViolation.filename.asc(), StyleViolation.message.asc()))

    assert len(results) == 3

    r1 = results[0]
    assert r1.filename == '/var/lib/jenkins/workspace/Releases/ESLint Release/eslint/fullOfProblems.js'
    assert r1.severity == Severity.error
    assert r1.message == "'addOne' is defined but never used. (no-unused-vars)"
    assert r1.source == 'eslint.rules.no-unused-vars'
    assert r1.lineno == 1
    assert r1.colno == 10
    r2 = results[1]
    assert r2.filename == '/var/lib/jenkins/workspace/Releases/ESLint Release/eslint/fullOfProblems.js'
    assert r2.severity == Severity.warning
    assert r2.message == "Missing semicolon. (semi)"
    assert r2.source == 'eslint.rules.semi'
    assert r2.lineno == 3
    assert r2.colno == 20
    r3 = results[2]
    assert r3.filename == '/var/lib/jenkins/workspace/Releases/ESLint Release/eslint/moreProblems.js'
    assert r3.severity == Severity.warning
    assert r3.message == "Unnecessary 'else' after 'return'. (no-else-return)"
    assert r3.source == 'eslint.rules.no-else-return'
    assert r3.lineno == 4
    assert r3.colno == 12
