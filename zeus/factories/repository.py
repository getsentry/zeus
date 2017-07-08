import factory
import factory.fuzzy

from zeus import models

from .types import GUIDFactory


class RepositoryFactory(factory.Factory):
    id = GUIDFactory()
    url = factory.fuzzy.FuzzyText(prefix='https://github.com/getsentry/', suffix='.git')
    name = factory.fuzzy.FuzzyText(prefix='getsentry/')
    backend = models.RepositoryBackend.git
    status = models.RepositoryStatus.active
    date_created = factory.Faker('date_time')

    class Meta:
        model = models.Repository
