import factory

from datetime import datetime, timedelta

from zeus import models

from .base import ModelFactory
from .types import GUIDFactory


class ApiTokenFactory(ModelFactory):
    id = GUIDFactory()

    class Meta:
        model = models.ApiToken

    class Params:
        expired = factory.Trait(
            expires_at=factory.LazyAttribute(lambda o: datetime.utcnow() - timedelta(days=1)),
        )
