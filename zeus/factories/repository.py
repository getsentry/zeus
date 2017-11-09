import factory
import factory.fuzzy

from zeus import models

from .base import ModelFactory
from .types import GUIDFactory

orgs = ('getsentry',)

names = ('sentry', 'zeus', 'raven-python', 'raven-php', 'raven-ruby', 'raven-js')


class RepositoryFactory(ModelFactory):
    id = GUIDFactory()
    owner_name = factory.Iterator(orgs)
    name = factory.Iterator(names)
    url = factory.LazyAttribute(
        lambda o: 'git@github.com:%s/%s.git' % (o.owner_name, o.name, ))
    backend = models.RepositoryBackend.git
    status = models.RepositoryStatus.active
    provider = models.RepositoryProvider.github
    external_id = factory.LazyAttribute(
        lambda o: '{}/{}'.format(o.owner_name, o.name))

    class Meta:
        model = models.Repository

    class Params:
        github = factory.Trait(
            provider=models.RepositoryProvider.github,
            external_id=factory.LazyAttribute(
                lambda o: '{}/{}'.format(o.owner_name, o.name)),
            data=factory.LazyAttribute(lambda o: {
                'full_name': '{}/{}'.format(o.owner_name, o.name),
            })
        )
