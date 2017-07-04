import factory

from zeus import models

from .types import GUIDFactory


class SourceFactory(factory.Factory):
    id = GUIDFactory()
    repository = factory.SubFactory('zeus.factories.RepositoryFactory')
    revision = factory.SubFactory(
        'zeus.factories.RevisionFactory', repository=factory.SelfAttribute('..repository'))

    class Meta:
        model = models.Source
