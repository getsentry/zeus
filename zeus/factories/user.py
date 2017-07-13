import factory

from zeus import models

from .base import ModelFactory
from .types import GUIDFactory


class UserFactory(ModelFactory):
    id = GUIDFactory()
    email = factory.Faker('email')

    class Meta:
        model = models.User
