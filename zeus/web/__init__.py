from flask import Blueprint

from . import hooks as h
from . import views as v

app = Blueprint('web', __name__)
app.add_url_rule(
    '/auth/github',
    view_func=v.GitHubLoginView.as_view('github-login', authorized_url='web.github-complete')
)
app.add_url_rule(
    '/auth/github/complete',
    view_func=v.GitHubCompleteView.as_view('github-complete', complete_url='web.index')
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
