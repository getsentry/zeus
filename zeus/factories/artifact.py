import factory

from zeus import models
from zeus.db.types.file import FileData

from .base import ModelFactory
from .types import GUIDFactory


class ArtifactFactory(ModelFactory):
    id = GUIDFactory()
    job = factory.SubFactory("zeus.factories.JobFactory")
    job_id = factory.SelfAttribute("job.id")
    repository = factory.SelfAttribute("job.repository")
    repository_id = factory.SelfAttribute("job.repository_id")
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

    class Meta:
        model = models.Artifact
