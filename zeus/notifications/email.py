from flask import current_app, render_template
from flask_mail import Message, sanitize_address
from typing import List

from zeus.config import db, mail
from zeus.constants import Result
from zeus.models import (
    Author, Build, Email, ItemOption, Job, Repository, RepositoryAccess,
    Revision, Source, StyleViolation, TestCase, User
)
from zeus.utils.email import inline_css


def find_linked_accounts(build: Build) -> List[User]:
    return list(User.query.join(
        Email, Email.user_id == User.id
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
    ))


def send_email_notification(build: Build):
    repo_options = dict(
        db.session.query(ItemOption.name, ItemOption.value).filter(
            ItemOption.item_id == build.repository_id,
            ItemOption.name.in_([
                'mail.notify_author',
            ])
        )
    )
    if repo_options.get('mail.notify_author') == '0':
        current_app.logger.info('mail.notify-author-disabled', extra={
            'build_id': build.id,
        })
        return

    msg = build_message(build)
    if not msg:
        return

    mail.send(msg)


def build_message(build: Build) -> Message:
    author = Author.query.join(
        Source, Source.author_id == Author.id,
    ).filter(
        Source.id == build.source_id,
    ).first()
    if not author:
        current_app.logger.info('mail.missing-author', extra={
            'build_id': build.id,
        })
        return

    users = find_linked_accounts(build)
    if not users:
        current_app.logger.info('mail.no-linked-accounts', extra={
            'build_id': build.id,
        })
        return

    # filter it down to the users that have notifications enabled
    user_options = dict(
        db.session.query(ItemOption.item_id, ItemOption.value).filter(
            ItemOption.item_id.in_([u.id for u in users]),
            ItemOption.name == 'mail.notify_author',
        )
    )
    users = [
        u for u in users
        if user_options.get(u.id, '1') == '1'
    ]
    if not users:
        current_app.logger.info('mail.no-enabed-accounts', extra={
            'build_id': build.id,
        })
        return

    source = Source.query.get(build.source_id)
    assert source

    repo = Repository.query.get(build.repository_id)
    assert repo

    revision = Revision.query.filter(
        Revision.sha == source.revision_sha,
        Revision.repository_id == build.repository_id,
    ).first()
    assert revision

    job_list = list(Job.query.filter(Job.build_id == build.id))
    job_ids = [j.id for j in job_list]

    recipients = [u.email for u in users]

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

        failing_tests_count = failing_tests_query.count()
        failing_tests = failing_tests_query.limit(10)

        style_violations_query = StyleViolation.query.filter(
            StyleViolation.job_id.in_(job_ids),
        )
        style_violations_count = style_violations_query.count()
        style_violations = style_violations_query.limit(10)
    else:
        failing_tests = ()
        failing_tests_count = 0
        style_violations = ()
        style_violations_count = 0

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
        } for test in failing_tests],
        'failing_tests_count': failing_tests_count,
        'style_violations': [{
            'message': violation.message,
            'filename': violation.filename
        } for violation in style_violations],
        'style_violations_count': style_violations_count,
    }

    msg = Message(subject, recipients=recipients, extra_headers={
        'Reply-To': ', '.join(sanitize_address(r) for r in recipients),
    })
    msg.body = render_template('notifications/email.txt', **context)
    msg.html = inline_css(
        render_template('notifications/email.html', **context)
    )

    return msg
