import factory

from zeus import models

from .base import ModelFactory
from .types import GUIDFactory

names = ('zeus', 'sentry', 'python', 'js', 'php')


class ProjectFactory(ModelFactory):
    id = GUIDFactory()
    repository = factory.SelfAttribute('zeus.factories.RepositoryFactory')
    repository_id = factory.SelfAttribute('repository.id')
    organization = factory.SelfAttribute('repository.organization')
    organization_id = factory.SelfAttribute('organization.id')
    name = factory.Iterator(names)

    class Meta:
        model = models.Project
