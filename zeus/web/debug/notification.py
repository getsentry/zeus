from flask import redirect, render_template, request
from jinja2 import Markup

from zeus import auth
from zeus.constants import Result
from zeus.models import Build
from zeus.notifications.email import build_message


class MailPreview(object):

    def __init__(self, msg):
        self.msg = msg

    @property
    def subject(self):
        return self.msg.subject

    def get_text_body(self):
        return self.msg.body

    def get_html_body(self):
        return Markup(self.msg.html)

    def render(self):
        return render_template(
            "debug/email.html", preview=self, format=request.args.get("format", "html")
        )


def debug_notification():
    if not auth.get_current_user():
        auth.bind_redirect_target(request.path)
        return redirect("/login")

    build = Build.query.filter(Build.result == Result.failed).order_by(
        Build.date_created.desc()
    ).limit(
        1
    ).first()
    assert build
    msg = build_message(build, force=True)
    assert msg
    preview = MailPreview(msg)
    return preview.render()
