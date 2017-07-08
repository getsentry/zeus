import factory
import factory.fuzzy

from zeus import models
from zeus.constants import Result

from .types import GUIDFactory


class TestCaseFactory(factory.Factory):
    id = GUIDFactory()
    name = factory.fuzzy.FuzzyText(prefix='tests.foo.bar')
    job = factory.SubFactory('zeus.factories.JobFactory')
    repository = factory.SelfAttribute('job.repository')
    result = Result.passed
    duration = factory.Faker('random_int', min=1, max=100000)
    date_created = factory.Faker('date_time')

    class Meta:
        model = models.TestCase
