from zeus.models import Artifact


def test_file_path(default_repo, default_job, default_testcase):
    artifact = Artifact(
        repository=default_repo,
        job=default_job,
        testcase=default_testcase,
    )
    assert artifact.file.path == 'artifacts'
