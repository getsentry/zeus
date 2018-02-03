import sqlparse

from flask_sqlalchemy import get_debug_queries
from flask_debugtoolbar.panels import DebugPanel


def format_sql(query, args):
    return sqlparse.format(query, reindent=True, keyword_case='upper')


class SQLAlchemyDebugPanel(DebugPanel):
    """
    Panel that displays the time a response took in milliseconds.
    """
    name = 'SQLAlchemy'

    def process_request(self, request):
        pass

    def process_response(self, request, response):
        pass

    def get_context(self):
        data = []
        for query in get_debug_queries():
            data.append({
                'duration': query.duration,
                'sql': format_sql(query.statement, query.parameters),
                'context': query.context
            })
        return {'queries': data}
