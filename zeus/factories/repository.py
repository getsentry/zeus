import factory
import factory.fuzzy

from faker import Factory
fake = Factory.create()

from zeus import models

from .types import GUIDFactory


class RepositoryFactory(factory.Factory):
    id = GUIDFactory()
    url = factory.LazyAttribute(
        lambda o: 'https://github.com/getsentry/%s.git' % (o.name.lower(), )
    )
    name = factory.LazyAttribute(lambda o: '%s/%s' % (fake.word(), fake.word()))
    backend = models.RepositoryBackend.git
    status = models.RepositoryStatus.active
    date_created = factory.Faker('date_time')

    class Meta:
        model = models.Repository
