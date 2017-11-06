from io import BytesIO

from zeus import factories
from zeus.artifacts.manager import Manager


def test_process_behavior(mocker, default_job):
    handler = mocker.Mock()
    handler.__name__ = 'CoverageHandler'

    manager = Manager()
    manager.register(handler, ['coverage.xml'])

    artifact = factories.ArtifactFactory(
        job=default_job,
        name='junit.xml',
    )
    artifact.file.save(BytesIO(), artifact.name)
    manager.process(artifact)

    assert not handler.called

    artifact = factories.ArtifactFactory(
        job=default_job,
        name='coverage.xml',
    )
    artifact.file.save(BytesIO(), artifact.name)
    manager.process(artifact)

    handler.assert_called_once_with(default_job)
    handler.return_value.process.assert_called_once()
