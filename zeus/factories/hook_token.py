import factory

from zeus import models

from .base import ModelFactory
from .types import GUIDFactory


class HookTokenFactory(ModelFactory):
    id = GUIDFactory()
    repository = factory.SubFactory('zeus.factories.RepositoryFactory')
    repository_id = factory.SelfAttribute('repository.id')

    class Meta:
        model = models.HookToken
