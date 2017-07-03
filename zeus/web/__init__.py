from flask import Blueprint

from . import views as v

app = Blueprint('web', __name__)
app.add_url_rule('/auth/github', view_func=v.GitHubLoginView.as_view(
    'github-login', authorized_url='web.github-complete'))
app.add_url_rule(
    '/auth/github/complete',
    view_func=v.GitHubCompleteView.as_view(
        'github-complete',
        complete_url='web.index'
    )
)
app.add_url_rule('/<path:path>', view_func=v.index)
app.add_url_rule('/', 'index', view_func=v.index)
