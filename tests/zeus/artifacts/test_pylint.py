from io import BytesIO

from zeus.artifacts.pylint import PyLintHandler
from zeus.constants import Severity
from zeus.models import StyleViolation


def test_pylint(sample_pylint, default_job):
    fp = BytesIO(sample_pylint.encode('utf8'))

    handler = PyLintHandler(default_job)
    handler.process(fp)

    results = list(StyleViolation.query.unrestricted_unsafe().filter(
        StyleViolation.job_id == default_job.id,
    ).order_by(StyleViolation.filename.asc(), StyleViolation.lineno.asc()))

    assert len(results) == 3

    r1 = results[0]
    assert r1.filename == 'zeus/bar.py'
    assert r1.severity == Severity.info
    assert r1.message == 'Missing module docstring'
    assert r1.source == 'C0111'
    assert r1.lineno == 1
    assert r1.colno is None
    r2 = results[1]
    assert r2.filename == 'zeus/foo.py'
    assert r2.severity == Severity.error
    assert r2.message == 'Exactly one space required around keyword argument assignment'
    assert r2.source == 'E0326'
    assert r2.lineno == 20
    assert r2.colno is None
    r3 = results[2]
    assert r3.filename == 'zeus/foo.py'
    assert r3.severity == Severity.warning
    assert r3.message == 'Line too long (112/100)'
    assert r3.source == 'W0301'
    assert r3.lineno == 200
    assert r3.colno is None
