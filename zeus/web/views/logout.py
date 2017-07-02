from flask import redirect, session, url_for
from flask.views import MethodView


class LogoutView(MethodView):
    def __init__(self, complete_url='/'):
        self.complete_url = complete_url
        super(LogoutView, self).__init__()

    def get(self):
        session.pop('uid', None)
        return redirect(url_for(self.complete_url))
