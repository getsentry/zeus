import factory

from zeus import models
from zeus.db.types import GUID


class SourceFactory(factory.Factory):
    id = factory.LazyFunction(GUID.default_value)
    repository = factory.SubFactory('zeus.factories.RepositoryFactory')
    revision = factory.SubFactory(
        'zeus.factories.RevisionFactory', repository=factory.SelfAttribute('..repository'))

    class Meta:
        model = models.Source
