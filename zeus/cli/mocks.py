import click

from random import choice, randint, random, randrange
from sqlalchemy.exc import IntegrityError

from zeus import factories, models
from zeus.api.schemas import BuildSchema
from zeus.config import db
from zeus.constants import Result, Status
from zeus.db.utils import try_create
from zeus.pubsub.utils import publish
from zeus.tasks import aggregate_build_stats_for_job

from .base import cli

build_schema = BuildSchema(strict=True)

repo_names = ('sentry', 'zeus')


def find_files_in_repo(repo):
    vcs = repo.get_vcs()
    vcs.ensure()
    result = [b for b in vcs.run(
        ['ls-tree', '-r', '--name-only', 'master']).split('\n') if b.endswith(('.py', '.js', 'jsx'))]
    assert result
    return result


def mock_single_repository(user_ids=()):
    repo = factories.RepositoryFactory.build(
        status=models.RepositoryStatus.active,
        github=True,
        owner_name='getsentry',
        name=choice(repo_names),
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


def mock_author(repo: models.Repository, user_id) -> models.Author:
    author = models.Author.query.unrestricted_unsafe().filter(
        models.Author.email.in_(
            db.session.query(models.Email.email).filter(
                models.Email.user_id == user_id
            )
        )
    ).first()
    if author:
        return author

    user = models.User.query.get(user_id)
    return factories.AuthorFactory(
        repository=repo,
        email=user.email,
    )


def mock_build(repo: models.Repository, parent_revision: models.Revision=None,
               user_ids=(), file_list=()):
    if user_ids and randint(0, 1) == 0:
        chosen_user_id = choice(user_ids)
        author = mock_author(repo, chosen_user_id)
    else:
        author = None

    revision = factories.RevisionFactory.create(
        repository=repo,
        parents=[parent_revision.sha] if parent_revision else None,
        **{'author': author} if author else {}
    )
    source = factories.SourceFactory.create(
        revision=revision,
        patch=factories.PatchFactory(
            parent_revision=parent_revision,
        ) if parent_revision and random() > 0.8 else None,
    )
    parent_revision = revision

    build = factories.BuildFactory.create(source=source, travis=True)

    result = build_schema.dump(build)
    publish('builds', 'build.create', result.data)
    click.echo('Created {!r}'.format(build))

    # we need to find some filenames for the repo
    if file_list is None:
        file_list = find_files_in_repo(repo)

    for n in range(randint(0, 50)):
        try:
            with db.session.begin_nested():
                factories.FileCoverageFactory.create(
                    filename=choice(file_list),
                    build=build, in_diff=randint(0, 5) == 0)
        except IntegrityError:
            continue

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
            if has_failure and randint(0, 2) == 0:
                for n in range(1, 5):
                    factories.StyleViolationFactory.create(
                        job=job,
                    )

        for n in range(randint(0, 2)):
            bundle = factories.BundleFactory.create(
                job=job,
            )
            for n in range(randint(0, 4)):
                factories.BundleAssetFactory.create(
                    bundle=bundle,
                    job=job,
                )

        artifact_count = randrange(3) \
            if job.status == Status.finished and job.result == Result.passed \
            else 0
        for n in range(0, artifact_count):
            factories.ArtifactFactory.create(job=job, repository=repo)

        db.session.commit()

        aggregate_build_stats_for_job(job_id=job.id)

        result = build_schema.dump(build)
        publish('builds', 'build.create', result.data)
        click.echo('Created {!r}'.format(build))

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
        file_list = find_files_in_repo(repo)

        parent_revision = None
        for n in range(10):
            build = mock_build(repo, parent_revision,
                               user_ids=user_ids, file_list=file_list)
            parent_revision = build.source.revision


@mocks.command()
def stream():
    user_ids = [u for u, in db.session.query(models.User.id)]
    repo = mock_single_repository(user_ids=user_ids)
    file_list = find_files_in_repo(repo)
    parent_revision = None
    while True:
        build = mock_build(repo, parent_revision,
                           user_ids=user_ids, file_list=file_list)
        parent_revision = build.source.revision
