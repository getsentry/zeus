import factory
import factory.fuzzy

from random import choice

from zeus import models

from .base import ModelFactory
from .types import GUIDFactory

names = ('culpa', 'ipsa', 'eum', 'alias')


class RepositoryFactory(ModelFactory):
    id = GUIDFactory()
    url = factory.LazyAttribute(lambda o: 'https://github.com/getsentry/%s.git' % (choice(names), ))
    backend = models.RepositoryBackend.git
    status = models.RepositoryStatus.active
    organization = factory.SubFactory('zeus.factories.OrganizationFactory')
    organization_id = factory.SelfAttribute('organization.id')

    class Meta:
        model = models.Repository
