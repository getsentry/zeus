import factory

from zeus import models

from .types import GUIDFactory


class UserFactory(factory.Factory):
    id = GUIDFactory()
    email = factory.Faker('email')

    class Meta:
        model = models.User
