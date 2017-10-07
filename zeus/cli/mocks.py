import click

from random import randint, random
from sqlalchemy.exc import IntegrityError

from zeus import factories, models
from zeus.config import db
from zeus.db.utils import try_create
from zeus.tasks import aggregate_build_stats_for_job

from .base import cli


def mock_single_repository(user_ids=()):
    repo = factories.RepositoryFactory.build(
        status=models.RepositoryStatus.active,
        github=True,
    )
    try:
        with db.session.begin_nested():
            db.session.add(repo)
    except IntegrityError:
        repo = models.Repository.query.unrestricted_unsafe().filter(
            models.Repository.provider == repo.provider,
            models.Repository.owner_name == repo.owner_name,
            models.Repository.name == repo.name
        ).first()
        click.echo('Using {!r}'.format(repo))
    else:
        click.echo('Created {!r}'.format(repo))

    for user_id in user_ids:
        try_create(models.RepositoryAccess, {
            'repository_id': repo.id,
            'user_id': user_id,
        })

    db.session.commit()
    return repo


def mock_build(repo: models.Repository, parent_revision: models.Revision=None):
    revision = factories.RevisionFactory.create(
        repository=repo,
        parents=[parent_revision.sha] if parent_revision else None,
    )
    source = factories.SourceFactory.create(
        revision=revision,
        patch=factories.PatchFactory(
            parent_revision=parent_revision,
        ) if parent_revision and random() > 0.8 else None,
    )
    parent_revision = revision
    build = factories.BuildFactory.create(source=source, travis=True)
    click.echo('Created {!r}'.format(build))

    for n in range(randint(0, 50)):
        factories.FileCoverageFactory.create(
            build=build, in_diff=randint(0, 5) == 0)

    for n in range(1, 4):
        has_failure = randint(0, 2) == 0
        job = factories.JobFactory.create(
            build=build,
            failed=has_failure,
            passed=not has_failure,
            travis=True,
            allow_failure=n == 3,
        )

        for n in range(randint(0, 50)):
            test_failed = has_failure and randint(0, 5) == 0
            factories.TestCaseFactory.create(
                job=job,
                failed=test_failed,
                passed=not test_failed,
            )
        db.session.commit()
        aggregate_build_stats_for_job(job_id=job.id)

    db.session.commit()
    return build


@cli.group('mocks')
def mocks():
    pass


@mocks.command('load-all')
def load_all():
    user_ids = [u for u, in db.session.query(models.User.id)]
    for n in range(3):
        repo = mock_single_repository(user_ids=user_ids)
        parent_revision = None
        for n in range(10):
            build = mock_build(repo, parent_revision)
            parent_revision = build.source.revision


@mocks.command()
def stream():
    user_ids = [u for u, in db.session.query(models.User.id)]
    repo = mock_single_repository(user_ids=user_ids)
    parent_revision = None
    while True:
        build = mock_build(repo, parent_revision)
        parent_revision = build.source.revision
