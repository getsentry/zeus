import factory

from zeus import models
from zeus.utils import timezone

from .base import ModelFactory
from .types import GUIDFactory


class UserFactory(ModelFactory):
    id = GUIDFactory()
    email = factory.Faker("email")
    date_created = factory.LazyAttribute(lambda o: timezone.now())
    date_active = factory.LazyAttribute(lambda o: o.date_created)

    class Meta:
        model = models.User
