# Based on Flask-SSLify, but stripped to what is needed
# and fixed to function with an app-factory

from flask import request, redirect, current_app

YEAR_IN_SECS = 31536000


class SSL(object):
    def __init__(self, app=None, age=YEAR_IN_SECS, subdomains=False):
        self.app = app
        self.hsts_age = age
        self.hsts_include_subdomains = subdomains

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config['PREFERRED_URL_SCHEME'] = 'https'
        app.config['SESSION_COOKIE_SECURE'] = True
        app.before_request(self.redirect_to_ssl)
        app.after_request(self.set_hsts_header)

    @property
    def hsts_header(self):
        """
        Returns the proper HSTS policy.
        """
        hsts_policy = 'max-age={0}'.format(self.hsts_age)
        if self.hsts_include_subdomains:
            hsts_policy += '; includeSubDomains'
        return hsts_policy

    def redirect_to_ssl(self):
        """
        Redirect incoming requests to HTTPS.
        """
        criteria = [
            request.is_secure,
            current_app.debug,
            current_app.testing,
            request.headers.get('X-Forwarded-Proto', 'http') == 'https'
        ]

        if not any(criteria):
            if request.url.startswith('http://'):
                url = request.url.replace('http://', 'https://', 1)
                r = redirect(url, code=301)
                return r

    def set_hsts_header(self, response):
        """
        Adds HSTS header to each response.
        """
        if request.is_secure:
            response.headers.setdefault('Strict-Transport-Security', self.hsts_header)
        return response
