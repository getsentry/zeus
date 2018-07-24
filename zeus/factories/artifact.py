import factory

from datetime import timedelta
from faker import Factory

from zeus import models
from zeus.constants import Status
from zeus.db.types.file import FileData
from zeus.utils import timezone

from .base import ModelFactory
from .types import GUIDFactory

faker = Factory.create()


class ArtifactFactory(ModelFactory):
    id = GUIDFactory()
    job = factory.SubFactory("zeus.factories.JobFactory")
    job_id = factory.SelfAttribute("job.id")
    repository = factory.SelfAttribute("job.repository")
    repository_id = factory.SelfAttribute("job.repository_id")
    status = factory.Iterator([Status.queued, Status.in_progress, Status.finished])
    name = factory.Faker("file_name")
    file = factory.LazyAttribute(
        lambda o: FileData(
            data={
                "filename": o.name,
                "storage": {"backend": "zeus.storage.mock.FileStorageCache"},
                "path": "mock/{}".format(o.name),
                "size": 2048,
            }
        )
    )
    date_created = factory.LazyAttribute(
        lambda o: timezone.now() - timedelta(minutes=30)
    )
    date_started = factory.LazyAttribute(
        lambda o: (
            faker.date_time_between(
                o.date_created, o.date_created + timedelta(minutes=1)
            )
            if o.status in [Status.finished, Status.in_progress]
            else None
        )
    )
    date_finished = factory.LazyAttribute(
        lambda o: faker.date_time_between(
            o.date_started, o.date_started + timedelta(minutes=10)
        )
        if o.status == Status.finished
        else None
    )
    date_updated = factory.LazyAttribute(
        lambda o: o.date_finished or o.date_started or o.date_created
    )

    class Meta:
        model = models.Artifact

    class Params:
        queued = factory.Trait(
            status=Status.queued, date_started=None, date_finished=None
        )
        in_progress = factory.Trait(status=Status.in_progress, date_finished=None)
        finished = factory.Trait(status=Status.finished)
