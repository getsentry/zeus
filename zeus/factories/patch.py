import factory
import os

from zeus import models

from .base import ModelFactory
from .types import GUIDFactory


class PatchFactory(ModelFactory):
    id = GUIDFactory()
    parent_revision = factory.SubFactory("zeus.factories.RevisionFactory")
    repository = factory.SelfAttribute("parent_revision.repository")
    repository_id = factory.SelfAttribute("parent_revision.repository_id")
    parent_revision_sha = factory.SelfAttribute("parent_revision.sha")
    diff = factory.LazyAttribute(
        lambda o: open(
            os.path.join(
                os.path.dirname(__file__),
                os.pardir,
                os.pardir,
                "tests",
                "fixtures",
                "sample.diff",
            )
        ).read()
    )

    class Meta:
        model = models.Patch
