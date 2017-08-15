from flask import current_app, render_template


def index(path=None):
    return render_template(
        'index.html', **{
            'SENTRY_DSN_FRONTEND': current_app.config.get('SENTRY_DSN_FRONTEND') or '',
            'SENTRY_ENVIRONMENT': current_app.config.get('SENTRY_ENVIRONMENT') or '',
            'SENTRY_RELEASE': current_app.config.get('SENTRY_RELEASE') or '',
        }
    )
