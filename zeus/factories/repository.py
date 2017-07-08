import factory

from zeus import models

from .types import GUIDFactory


class RepositoryFactory(factory.Factory):
    id = GUIDFactory()
    url = 'https://github.com/getsentry/zeus.git'
    backend = models.RepositoryBackend.git
    status = models.RepositoryStatus.active
    date_created = factory.Faker('date_time')

    class Meta:
        model = models.Repository
