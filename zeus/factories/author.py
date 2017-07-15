import factory
import factory.faker

from zeus import models

from .base import ModelFactory


class AuthorFactory(ModelFactory):
    organization = factory.SubFactory('zeus.factories.OrganizationFactory')
    organization_id = factory.SelfAttribute('organization.id')
    name = factory.Faker('first_name')
    email = factory.Faker('email')

    class Meta:
        model = models.Author
