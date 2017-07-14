import factory
import factory.faker

from zeus import models

from .base import ModelFactory


class RevisionFactory(ModelFactory):
    sha = factory.Faker('sha1')
    repository = factory.SubFactory('zeus.factories.RepositoryFactory')
    repository_id = factory.SelfAttribute('repository.id')
    author = factory.SubFactory(
        'zeus.factories.AuthorFactory', organization=factory.SelfAttribute('..organization')
    )
    author_id = factory.SelfAttribute('author.id')
    message = factory.faker.Faker('sentence')
    organization = factory.SelfAttribute('repository.organization')
    organization_id = factory.SelfAttribute('organization.id')

    class Meta:
        model = models.Revision
