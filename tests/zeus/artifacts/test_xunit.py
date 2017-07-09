from io import BytesIO

from zeus.artifacts.xunit import XunitHandler
from zeus.constants import Result
from zeus.models import Job
from zeus.utils.testresult import TestResult as ZeusTestResult


def test_result_generation(sample_xunit):
    job = Job()

    fp = BytesIO(sample_xunit.encode('utf8'))

    handler = XunitHandler(job)
    results = handler.get_tests(fp)

    assert len(results) == 2

    r1 = results[0]
    assert type(r1) == ZeusTestResult
    assert r1.job == job
    assert r1.name == 'tests.test_report'
    assert r1.duration == 0.0
    assert r1.result == Result.failed
    assert r1.message == """tests/test_report.py:1: in <module>
>   import mock
E   ImportError: No module named mock"""
    r2 = results[1]
    assert type(r2) == ZeusTestResult
    assert r2.job == job
    assert r2.name == 'tests.test_report.ParseTestResultsTest.test_simple'
    assert r2.duration == 1.65796279907
    assert r2.result == Result.passed
    assert r2.message == ''
