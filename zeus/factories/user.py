import factory

from zeus import models

from .types import GUIDFactory


class UserFactory(factory.Factory):
    id = GUIDFactory()
    email = factory.Faker('email')
    date_created = factory.Faker('date_time')

    class Meta:
        model = models.User
