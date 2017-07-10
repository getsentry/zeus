import factory
import factory.fuzzy

from random import choice

from zeus import models

from .base import ModelFactory
from .types import GUIDFactory

orgs = ('ab', 'vitae')

names = ('culpa', 'ipsa', 'eum', 'alias')


class RepositoryFactory(ModelFactory):
    id = GUIDFactory()
    url = factory.LazyAttribute(
        lambda o: 'https://github.com/getsentry/%s.git' % (o.name.lower(), )
    )
    name = factory.LazyAttribute(lambda o: '%s%s' % (choice(orgs), choice(names)))
    backend = models.RepositoryBackend.git
    status = models.RepositoryStatus.active
    date_created = factory.Faker('date_time')

    class Meta:
        model = models.Repository
