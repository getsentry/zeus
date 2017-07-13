import factory
import os

from zeus import models

from .base import ModelFactory
from .types import GUIDFactory


class PatchFactory(ModelFactory):
    id = GUIDFactory()
    parent_revision = factory.SubFactory('zeus.factories.RevisionFactory')
    diff = factory.LazyAttribute(lambda o: open(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'tests', 'fixtures', 'sample.diff')
    ).read())
    date_created = factory.Faker('date_time')

    # automatically populated from revision
    repository = factory.SelfAttribute('parent_revision.repository')
    repository_id = factory.SelfAttribute('parent_revision.repository_id')
    parent_revision_sha = factory.SelfAttribute('parent_revision.sha')

    class Meta:
        model = models.Patch
