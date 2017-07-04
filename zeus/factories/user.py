import factory

from zeus import models
from zeus.db.types import GUID


class UserFactory(factory.Factory):
    id = factory.LazyFunction(GUID.default_value)
    email = factory.Faker('email')

    class Meta:
        model = models.User
