from flask import Blueprint

from zeus.constants import GITHUB_DEFAULT_SCOPES

from . import hooks as h
from . import views as v

from ..providers.travis.webhook import TravisWebhookView

app = Blueprint('web', __name__)
app.add_url_rule(
    '/auth/github',
    view_func=v.GitHubAuthView.as_view(
        'github-auth',
        authorized_url='web.github-complete',
        scopes=GITHUB_DEFAULT_SCOPES,
    ),
)
app.add_url_rule(
    '/auth/github/complete',
    view_func=v.GitHubCompleteView.as_view('github-complete')
)
app.add_url_rule(
    '/hooks/<hook_id>/public/provider/travis/webhook',
    view_func=TravisWebhookView.as_view('travis-webhook')
)
app.add_url_rule(
    '/hooks/<hook_id>/<signature>/builds/<build_xid>', view_func=h.BuildHook.as_view('build-hook')
)
app.add_url_rule(
    '/hooks/<hook_id>/<signature>/builds/<build_xid>/jobs/<job_xid>',
    view_func=h.JobHook.as_view('job-hook')
)
app.add_url_rule(
    '/hooks/<hook_id>/<signature>/builds/<build_xid>/jobs/<job_xid>/artifacts',
    view_func=h.JobArtifactsHook.as_view('job-artifacts-hook')
)
app.add_url_rule('/<path:path>', view_func=v.index)
app.add_url_rule('/', 'index', view_func=v.index)
