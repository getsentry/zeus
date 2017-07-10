import factory
import factory.faker

from zeus import models

from .base import ModelFactory


class AuthorFactory(ModelFactory):
    repository = factory.SubFactory('zeus.factories.RepositoryFactory')
    repository_id = factory.SelfAttribute('repository.id')
    name = factory.Faker('first_name')
    email = factory.Faker('email')
    date_created = factory.Faker('date_time')

    class Meta:
        model = models.Author
