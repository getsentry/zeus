import factory
import factory.fuzzy

from faker import Factory
faker = Factory.create()

from zeus import models

from .base import ModelFactory
from .types import GUIDFactory


class BundleEntrypointFactory(ModelFactory):
    id = GUIDFactory()
    name = factory.LazyAttribute(
        lambda o: faker.word()
    )
    job = factory.SubFactory('zeus.factories.JobFactory')
    job_id = factory.SelfAttribute('job.id')
    repository = factory.SelfAttribute('job.repository')
    repository_id = factory.SelfAttribute('repository.id')

    class Meta:
        model = models.BundleEntrypoint


class BundleAssetFactory(ModelFactory):
    id = GUIDFactory()
    name = factory.LazyAttribute(
        lambda o: faker.word()
    )
    job = factory.SubFactory('zeus.factories.JobFactory')
    job_id = factory.SelfAttribute('job.id')
    repository = factory.SelfAttribute('job.repository')
    repository_id = factory.SelfAttribute('repository.id')
    size = factory.Faker('random_int', min=50, max=1000000)

    class Meta:
        model = models.BundleAsset
