from flask import render_template, request
from jinja2 import Markup

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
            'debug/email.html',
            preview=self,
            format=request.args.get('format', 'html'),
        )


def debug_notification():
    build = Build.query.order_by(Build.date_created.desc()).limit(1).first()
    msg = build_message(build)
    preview = MailPreview(msg)
    return preview.render()
