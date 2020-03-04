from zeus import factories


def test_revision_failures_list(
    client,
    sqla_assertions,
    db_session,
    default_login,
    default_repo,
    default_build,
    default_revision,
    default_repo_access,
):
    job1 = factories.JobFactory(build=default_build)
    job2 = factories.JobFactory(build=default_build)
    db_session.add(job1)
    db_session.add(job2)

    failure1 = factories.FailureReasonFactory(job=job1, failing_tests=True)
    failure2 = factories.FailureReasonFactory(job=job2, missing_tests=True)
    failure3 = factories.FailureReasonFactory(job=job2, failing_tests=True)
    db_session.add(failure1)
    db_session.add(failure2)
    db_session.add(failure3)

    resp = client.get(
        "/api/repos/{}/revisions/{}/failures".format(
            default_repo.get_full_name(), default_revision.sha
        )
    )

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["reason"] == "failing_tests"
    assert data[0]["runs"] == [
        {"id": str(failure3.id), "job_id": str(job2.id)},
        {"id": str(failure1.id), "job_id": str(job1.id)},
    ]
    assert data[1]["reason"] == "missing_tests"
    assert data[1]["runs"] == [{"id": str(failure2.id), "job_id": str(job2.id)}]
