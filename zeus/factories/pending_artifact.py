import factory

from datetime import timedelta
from io import BytesIO
from faker import Factory
from random import randint

from zeus import models
from zeus.db.types.file import FileData
from zeus.utils import timezone

from .base import ModelFactory
from .types import GUIDFactory

faker = Factory.create()


def make_file_data(o):
    fd = FileData(
        data={
            "filename": o.name,
            "storage": {"backend": "zeus.storage.mock.FileStorageCache"},
            "path": "mock/{}".format(o.name),
            "size": 2048,
        }
    )
    fd.save(BytesIO(b""))
    return fd


class PendingArtifactFactory(ModelFactory):
    id = GUIDFactory()
    hook = factory.SubFactory("zeus.factories.HookFactory")
    hook_id = factory.SelfAttribute("hook.id")

    repository = factory.SelfAttribute("hook.repository")
    repository_id = factory.SelfAttribute("hook.repository.id")

    provider = factory.SelfAttribute("hook.provider")
    external_build_id = factory.LazyAttribute(lambda o: str(randint(10000, 999999)))
    external_job_id = factory.LazyAttribute(lambda o: str(randint(10000, 999999)))
    name = factory.Faker("file_name")
    file = factory.LazyAttribute(make_file_data)
    date_created = factory.LazyAttribute(
        lambda o: timezone.now() - timedelta(minutes=30)
    )

    class Meta:
        model = models.PendingArtifact
