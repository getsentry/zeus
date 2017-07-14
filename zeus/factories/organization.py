import factory

from zeus import models

from .base import ModelFactory
from .types import GUIDFactory

names = ('getsentry', 'sentry')


class OrganizationFactory(ModelFactory):
    id = GUIDFactory()
    name = factory.Iterator(names)

    class Meta:
        model = models.Organization
