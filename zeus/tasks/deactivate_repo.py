from enum import Enum
from flask import current_app, render_template
from flask_mail import Message, sanitize_address
from uuid import UUID

from zeus.config import celery, db, mail
from zeus.constants import Permission
from zeus.models import ItemOption, Repository, RepositoryAccess, RepositoryStatus, User
from zeus.utils.email import inline_css
from zeus.utils.http import absolute_url


class DeactivationReason(Enum):
    invalid_pubkey = "invalid_pubkey"


@celery.task(max_retries=5, autoretry_for=(Exception,), acks_late=True, time_limit=60)
def deactivate_repo(repository_id: UUID, reason: DeactivationReason):
    repository = Repository.query.unrestricted_unsafe().get(repository_id)

    repository.status = RepositoryStatus.inactive
    with db.session.begin_nested():
        ItemOption.query.filter(
            ItemOption.item_id == repository_id, ItemOption.name == "auth.private-key"
        ).delete()
        db.session.add(repository)

    current_app.logger.warn(
        "repository.deactivated repository_id=%s reason=%s", repository_id, reason
    )
    db.session.commit()

    msg = build_message(repository, reason)
    if msg:
        mail.send(msg)


def build_message(repository: Repository, reason: DeactivationReason) -> Message:
    recipients = [
        e
        for e, in db.session.query(User.email).filter(
            User.id.in_(
                db.session.query(RepositoryAccess.user_id).filter(
                    RepositoryAccess.repository_id == repository.id,
                    RepositoryAccess.permission == Permission.admin,
                )
            )
        )
    ]
    if not recipients:
        current_app.logger.warn(
            "email.deactivated-repository.no-recipients repository_id=%s", repository.id
        )
        return

    context = {
        "title": "Repository Disabled",
        "settings_url": absolute_url("/settings/github/repos"),
        "repo": {
            "owner_name": repository.owner_name,
            "name": repository.name,
            "full_name": repository.get_full_name,
        },
        "reason": reason,
    }

    msg = Message(
        "Repository Disabled - {}/{}".format(repository.owner_name, repository.name),
        recipients=recipients,
        extra_headers={"Reply-To": ", ".join(sanitize_address(r) for r in recipients)},
    )
    msg.body = render_template("emails/deactivated-repository.txt", **context)
    msg.html = inline_css(
        render_template("emails/deactivated-repository.html", **context)
    )

    return msg
