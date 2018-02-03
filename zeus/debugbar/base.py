import json

from flask import request

import flask_debugtoolbar


class DebugToolbarExtension(flask_debugtoolbar.DebugToolbarExtension):
    def _default_config(self, app):
        return {
            'DEBUG_TB_ENABLED': app.debug,
            'DEBUG_TB_HOSTS': (),
            'DEBUG_TB_INTERCEPT_REDIRECTS': True,
            'DEBUG_TB_PANELS': (
                'zeus.debugbar.panels.sqlalchemy.SQLAlchemyDebugPanel',
                # 'flask_debugtoolbar.panels.timer.TimerDebugPanel',
                # 'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
                # 'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
                # 'flask_debugtoolbar.panels.config_vars.ConfigVarsDebugPanel',
                # 'flask_debugtoolbar.panels.template.TemplateDebugPanel',
                # 'flask_debugtoolbar.panels.sqlalchemy.SQLAlchemyDebugPanel',
                # 'flask_debugtoolbar.panels.logger.LoggingPanel',
                # 'flask_debugtoolbar.panels.route_list.RouteListDebugPanel',
                # 'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',
            ),
        }

    def process_response(self, response):
        real_request = request._get_current_object()
        if real_request not in self.debug_toolbars:
            return response

        toolbar = self.debug_toolbars[real_request]

        for panel in toolbar.panels:
            panel.process_response(real_request, response)
        return self.encode_response(response, toolbar)

    def encode_response(self, response, toolbar):
        for panel in toolbar.panels:
            context = panel.get_context()
            if context:
                header_name = 'Debug-{}'.format(panel.name.replace(' ', ''))
                response.headers[header_name] = json.dumps(context)
        return response
