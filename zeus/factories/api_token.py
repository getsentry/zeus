import factory

from datetime import timedelta

from zeus import models
from zeus.utils import timezone

from .base import ModelFactory
from .types import GUIDFactory


class ApiTokenFactory(ModelFactory):
    id = GUIDFactory()

    class Meta:
        model = models.ApiToken

    class Params:
        expired = factory.Trait(
            expires_at=factory.LazyAttribute(
                lambda o: timezone.now() - timedelta(days=1)
            )
        )
