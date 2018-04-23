from flask import Blueprint

from .notification import debug_notification

app = Blueprint("debug", __name__)
app.add_url_rule("/mail/notification", view_func=debug_notification)
