import factory
import factory.fuzzy

from faker import Factory
faker = Factory.create()

from zeus import models

from .types import GUIDFactory


class FileCoverageFactory(factory.Factory):
    id = GUIDFactory()
    filename = factory.LazyAttribute(
        lambda o: 'tests/%s/%s/%s.py' % (faker.word(), faker.word(), faker.word())
    )
    job = factory.SubFactory('zeus.factories.JobFactory')
    job_id = factory.SelfAttribute('job.id')
    repository = factory.SelfAttribute('job.repository')
    repository_id = factory.SelfAttribute('job.repository_id')
    data = 'CCCUUUU'
    date_created = factory.Faker('date_time')

    class Meta:
        model = models.FileCoverage
