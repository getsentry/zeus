import factory

from zeus import models

from .base import ModelFactory
from .types import GUIDFactory


class HookFactory(ModelFactory):
    id = GUIDFactory()
    project = factory.SubFactory('zeus.factories.ProjectFactory')
    project_id = factory.SelfAttribute('project.id')
    organization = factory.SelfAttribute('project.organization')
    organization_id = factory.SelfAttribute('organization.id')
    provider = 'travis'

    class Meta:
        model = models.Hook
