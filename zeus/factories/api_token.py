import factory

from datetime import datetime, timedelta, timezone

from zeus import models

from .base import ModelFactory
from .types import GUIDFactory


class ApiTokenFactory(ModelFactory):
    id = GUIDFactory()

    class Meta:
        model = models.ApiToken

    class Params:
        expired = factory.Trait(
            expires_at=factory.
            LazyAttribute(lambda o: datetime.now(timezone.utc) - timedelta(days=1)),
        )
