import factory

from zeus import models
from zeus.db.types import GUID


class RepositoryFactory(factory.Factory):
    id = factory.LazyFunction(GUID.default_value)
    url = 'https://github.com/getsentry/zeus.git'
    backend = models.RepositoryBackend.git
    status = models.RepositoryStatus.active

    class Meta:
        model = models.Repository
