import factory

from zeus import models

from .base import ModelFactory
from .types import GUIDFactory


class EmailFactory(ModelFactory):
    id = GUIDFactory()
    user = factory.SubFactory('zeus.factories.UserFactory')
    user_id = factory.SelfAttribute('user.id')
    email = factory.Faker('email')
    verified = True

    class Meta:
        model = models.Email
