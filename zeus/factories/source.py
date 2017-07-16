import factory

from zeus import models

from .base import ModelFactory
from .types import GUIDFactory


class SourceFactory(ModelFactory):
    id = GUIDFactory()
    revision = factory.SubFactory('zeus.factories.RevisionFactory')
    repository = factory.SelfAttribute('revision.repository')
    repository_id = factory.SelfAttribute('revision.repository_id')
    revision_sha = factory.SelfAttribute('revision.sha')
    author = factory.SelfAttribute('revision.author')
    author_id = factory.SelfAttribute('author.id')

    class Meta:
        model = models.Source
