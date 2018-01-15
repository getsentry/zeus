from io import BytesIO

from zeus.artifacts.gotest import GoTestHandler
from zeus.constants import Result
from zeus.models import Job
from zeus.utils.testresult import TestResult as ZeusTestResult


def test_result_generation(sample_gotest):
    job = Job()

    fp = BytesIO(sample_gotest.encode('utf8'))

    handler = GoTestHandler(job)
    results = handler.get_tests(fp)

    assert len(results) == 3

    r1 = results[0]
    assert type(r1) == ZeusTestResult
    assert r1.job == job
    assert r1.name == 'golang.org/x/sync/syncmap/TestMapMatchesRWMutex'
    assert r1.duration == 10.0
    assert r1.result == Result.passed
    assert r1.message is None
    r2 = results[1]
    assert type(r2) == ZeusTestResult
    assert r2.job == job
    assert r2.name == 'golang.org/x/sync/syncmap/TestMapMatchesDeepCopy'
    assert r2.duration == 10.0
    assert r2.result == Result.passed
    assert r2.message is None
    r3 = results[2]
    assert type(r3) == ZeusTestResult
    assert r3.job == job
    assert r3.name == 'golang.org/x/sync/syncmap/TestConcurrentRange'
    assert r3.duration == 0.0
    assert r3.result == Result.failed
    assert r3.message == '\tmap_test.go:169: Range visited 1024 elements of 1024-element Map\n'
