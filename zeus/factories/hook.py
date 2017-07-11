import factory

from zeus import models

from .base import ModelFactory
from .types import GUIDFactory


class HookFactory(ModelFactory):
    id = GUIDFactory()
    repository = factory.SubFactory('zeus.factories.RepositoryFactory')
    repository_id = factory.SelfAttribute('repository.id')
    provider = 'travis'

    class Meta:
        model = models.Hook
