from flask import Blueprint

from . import views as v

app = Blueprint('web', __name__)
app.add_url_rule('/', view_func=v.index)
app.add_url_rule('/auth/github', view_func=v.GitHubLoginView)
app.add_url_rule('/auth/github/complete', view_func=v.GitHubCompleteView)
