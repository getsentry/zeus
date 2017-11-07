from flask import current_app, render_template
from flask_mail import Message, sanitize_address

from zeus.config import db, mail
from zeus.constants import Result
from zeus.models import Author, Build, Email, ItemOption, Job, Repository, RepositoryAccess, Revision, Source, TestCase, User
from zeus.utils.email import inline_css


def has_linked_account(build: Build) -> bool:
    return db.session.query(
        db.session.query(Email.email).join(
            User, Email.user_id == User.id
        ).join(
            RepositoryAccess, RepositoryAccess.user_id == User.id
        ).join(
            Source, Source.id == build.source_id
        ).join(
            Author, Source.author_id == Author.id
        ).filter(
            Email.email == Author.email,
            Email.verified == True,  # NOQA
            RepositoryAccess.repository_id == build.repository_id,
        ).exists()
    ).scalar()


def send_email_notification(build: Build):
    if build.result != Result.failed:
        return

    options = dict(
        db.session.query(ItemOption.name, ItemOption.value).filter(
            ItemOption.item_id == build.repository_id,
            ItemOption.name.in_([
                'mail.notify-author',
            ])
        )
    )
    if options.get('mail.notify-author') == '0':
        return

    if not has_linked_account(build):
        return

    msg = build_message(build)
    mail.send(msg)


def build_message(build: Build) -> Message:
    source = Source.query.get(build.source_id)
    assert source
    revision = Revision.query.filter(
        Revision.sha == source.revision_sha,
        Revision.repository_id == build.repository_id,
    ).first()
    assert revision
    author = Author.query.join(
        Source, Source.author_id == Author.id,
    ).filter(
        Source.id == build.source_id,
    ).first()
    assert author

    repo = Repository.query.get(build.repository_id)
    assert repo

    job_list = list(Job.query.filter(Job.build_id == build.id))
    job_ids = [j.id for j in job_list]

    recipients = [author.email]

    subject = 'Build {} - {}/{} #{}'.format(
        str(build.result).title(),
        repo.owner_name,
        repo.name,
        build.number,
    )

    if job_ids:
        failing_tests_query = TestCase.query.filter(
            TestCase.job_id.in_(job_ids),
            TestCase.result == Result.failed,
        )
    else:
        failing_tests_query = TestCase.query.none()

    failing_tests_count = failing_tests_query.count()

    context = {
        'title': subject,
        'uri': '{proto}://{domain}/{repo}/builds/{build_no}'.format(
            proto='https' if current_app.config['SSL'] else 'http',
            domain=current_app.config['DOMAIN'],
            repo=repo.get_full_name(),
            build_no=build.number,
        ),
        'build': {
            'number': build.number,
            'result': {
                'id': str(build.result),
                'name': str(build.result).title(),
            },
            'label': build.label,
        },
        'repo': {
            'owner_name': repo.owner_name,
            'name': repo.name,
            'full_name': repo.get_full_name,
        },
        'author': {
            'name': author.name,
            'email': author.email,
        },
        'revision': {
            'sha': revision.sha,
            'short_sha': revision.sha[:7],
            'message': revision.message,
        },
        'job_list': [{
            'number': job.number,
            'result': {
                'id': str(build.result),
                'name': str(build.result).title(),
            },
            'url': job.url,
            'label': job.label,
        } for job in job_list],
        'job_failure_count': sum((1 for job in job_list if job.result == Result.failed)),
        'date_created': build.date_created,
        'failing_tests': [{
            'name': test.name
        } for test in failing_tests_query.limit(10)],
        'failing_tests_count': failing_tests_count,
    }

    msg = Message(subject, recipients=recipients, extra_headers={
        'Reply-To': ', '.join(sanitize_address(r) for r in recipients),
    })
    msg.body = render_template('notifications/email.txt', **context)
    msg.html = inline_css(
        render_template('notifications/email.html', **context)
    )

    return msg
