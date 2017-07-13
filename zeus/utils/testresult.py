import re

from flask import current_app
from sqlalchemy.sql import func

from zeus.config import db
from zeus.constants import Result
from zeus.db.utils import create_or_update
from zeus.models import Artifact, ItemStat, TestCase
from zeus.utils import timezone


class TestResult(object):
    """
    A helper class which ensures that TestSuite instances are
    managed correctly when TestCase's are created.
    """

    def __init__(
        self,
        job,
        name,
        message=None,
        package=None,
        result=None,
        duration=None,
        date_created=None,
        artifacts=None
    ):
        self.job = job
        self._name = name
        self._package = package
        self.message = message
        self.result = result or Result.unknown
        self.duration = duration  # ms
        self.date_created = date_created or timezone.now()
        self.artifacts = artifacts

    @property
    def sep(self):
        name = (self._package or self._name)
        # handle the case where it might begin with some special character
        if not re.match(r'^[a-zA-Z0-9]', name):
            return '/'
        elif '/' in name:
            return '/'
        return '.'

    @property
    def hash(self):
        return TestCase.calculate_sha(self.name)

    @property
    def name(self):
        if self._package:
            return "%s%s%s" % (self._package, self.sep, self._name)
        return self._name

    id = name


class TestResultManager(object):
    def __init__(self, job):
        self.job = job

    def clear(self):
        """
        Removes all existing test data from this job.
        """
        TestCase.query.filter(
            TestCase.job_id == self.job.id,
        )

    def save(self, test_list):
        if not test_list:
            return

        job = self.job
        repository_id = job.repository_id

        # create all test cases
        for test in test_list:
            testcase = TestCase(
                job=job,
                repository_id=repository_id,
                hash=test.hash,
                name=test.name,
                duration=test.duration,
                message=test.message,
                result=test.result,
                date_created=test.date_created,
            )
            db.session.add(testcase)

            if test.artifacts:
                for ta in test.artifacts:
                    testartifact = Artifact(
                        repository_id=repository_id,
                        testcase_id=testcase.id,
                        job_id=job.id,
                        name=ta['name'],
                        # TODO(dcramer): mimetype detection?
                        # type=getattr(Artifactta['type'],
                    )
                    testartifact.save_base64_content(ta['base64'])
                    db.session.add(testartifact)

        db.session.commit()

        try:
            self._record_test_counts(test_list)
            self._record_test_failures(test_list)
            self._record_test_duration(test_list)
        except Exception:
            current_app.logger.exception('Failed to record aggregate test statistics')

    def _record_test_counts(self, test_list):
        create_or_update(
            ItemStat,
            where={
                'item_id': self.job.id,
                'name': 'tests.count',
            },
            values={
                'value':
                db.session.query(func.count(TestCase.id)).filter(
                    TestCase.job_id == self.job.id,
                ).as_scalar(),
            }
        )
        db.session.commit()

    def _record_test_failures(self, test_list):
        create_or_update(
            ItemStat,
            where={
                'item_id': self.job.id,
                'name': 'tests.failures',
            },
            values={
                'value':
                db.session.query(func.count(TestCase.id)).filter(
                    TestCase.job_id == self.job.id,
                    TestCase.result == Result.failed,
                ).as_scalar(),
            }
        )
        db.session.commit()

    def _record_test_duration(self, test_list):
        create_or_update(
            ItemStat,
            where={
                'item_id': self.job.id,
                'name': 'tests.duration',
            },
            values={
                'value':
                db.session.query(func.coalesce(func.sum(TestCase.duration), 0)).filter(
                    TestCase.job_id == self.job.id,
                ).as_scalar(),
            }
        )
