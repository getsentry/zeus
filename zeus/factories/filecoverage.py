import factory
import factory.fuzzy

from faker import Factory
faker = Factory.create()

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
    repository_id = factory.SelfAttribute('job.repository_id')
    data = 'CCCUUUU'
    lines_covered = 3
    lines_uncovered = 4
    diff_lines_covered = 3
    diff_lines_uncovered = 3
    date_created = factory.Faker('date_time')

    class Meta:
        model = models.FileCoverage
