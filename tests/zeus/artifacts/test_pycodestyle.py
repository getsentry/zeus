from io import BytesIO

from zeus.artifacts.pycodestyle import PyCodeStyleHandler
from zeus.constants import Severity
from zeus.models import StyleViolation


def test_pep8(sample_pep8, default_job):
    fp = BytesIO(sample_pep8.encode("utf8"))

    handler = PyCodeStyleHandler(default_job)
    handler.process(fp)

    results = list(
        StyleViolation.query.unrestricted_unsafe()
        .filter(StyleViolation.job_id == default_job.id)
        .order_by(StyleViolation.filename.asc(), StyleViolation.lineno.asc())
    )

    assert len(results) == 2

    r1 = results[0]
    assert r1.filename == "optparse.py"
    assert r1.severity == Severity.error
    assert r1.message == "multiple imports on one line"
    assert r1.source == "E401"
    assert r1.lineno == 69
    assert r1.colno == 11
    r2 = results[1]
    assert r2.filename == "optparse.py"
    assert r2.severity == Severity.warning
    assert r2.message == "expected 2 blank lines, found 1"
    assert r2.source == "W302"
    assert r2.lineno == 77
    assert r2.colno == 1
