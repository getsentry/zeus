import factory
import factory.faker

from zeus import models

from .base import ModelFactory


class RevisionFactory(ModelFactory):
    sha = factory.Faker('sha1')
    repository = factory.SubFactory('zeus.factories.RepositoryFactory')
    repository_id = factory.SelfAttribute('repository.id')
    author = factory.SubFactory(
        'zeus.factories.AuthorFactory', repository=factory.SelfAttribute('..repository')
    )
    author_id = factory.SelfAttribute('author.id')
    message = factory.faker.Faker('sentence')
    date_created = factory.Faker('date_time')
    date_committed = factory.Faker('date_time')

    class Meta:
        model = models.Revision
