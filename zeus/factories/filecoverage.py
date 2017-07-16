import factory
import factory.fuzzy

from faker import Factory
faker = Factory.create()

from random import randint
from zeus import models

from .base import ModelFactory
from .types import GUIDFactory


class FileCoverageFactory(ModelFactory):
    id = GUIDFactory()
    filename = factory.LazyAttribute(
        lambda o: 'tests/%s/%s/%s.py' % (faker.word(), faker.word(), faker.word())
    )
    job = factory.SubFactory('zeus.factories.JobFactory')
    job_id = factory.SelfAttribute('job.id')
    repository = factory.SelfAttribute('job.repository')
    repository_id = factory.SelfAttribute('repository.id')
    data = 'CCCUUUU'
    lines_covered = factory.Faker('random_int', min=0, max=100)
    lines_uncovered = factory.Faker('random_int', min=0, max=100)
    diff_lines_covered = 0
    diff_lines_uncovered = 0

    class Meta:
        model = models.FileCoverage

    class Params:
        in_diff = factory.Trait(
            diff_lines_covered=factory.
            LazyAttribute(lambda o: max(o.lines_covered - randint(0, 3), 0)),
            diff_lines_uncovered=factory.
            LazyAttribute(lambda o: max(o.lines_covered - randint(0, 5), 0)),
        )
