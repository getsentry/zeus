import factory
import factory.fuzzy

from faker import Factory
faker = Factory.create()

from zeus import models
from zeus.constants import Result

from .base import ModelFactory
from .types import GUIDFactory


class TestCaseFactory(ModelFactory):
    id = GUIDFactory()
    name = factory.LazyAttribute(
        lambda o: 'tests.%s.%s.%s' % (faker.word(), faker.word(), faker.word())
    )
    job = factory.SubFactory('zeus.factories.JobFactory')
    job_id = factory.SelfAttribute('job.id')
    repository = factory.SelfAttribute('job.repository')
    repository_id = factory.SelfAttribute('repository.id')
    result = factory.Iterator([Result.failed, Result.passed])
    duration = factory.Faker('random_int', min=1, max=100000)
    date_created = factory.Faker('date_time')

    class Meta:
        model = models.TestCase

    class Params:
        failed = factory.Trait(
            result=Result.failed,
        )
        passed = factory.Trait(
            result=Result.passed,
        )
