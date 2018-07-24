from datetime import timedelta
from flask import current_app

from zeus.models import Build, User, Repository
from zeus.utils import timezone

from .base import Resource


class InstallIndexResource(Resource):
    auth_required = False

    def get(self):
        """
        Return various details about the installation.
        """
        return {
            "config": {
                "debug": current_app.debug,
                "environment": current_app.config["SENTRY_ENVIRONMENT"],
                "release": current_app.config["SENTRY_RELEASE"],
                "streamUrl": current_app.config["STREAM_URL"],
            },
            "stats": {
                "buildsTotal": Build.query.unrestricted_unsafe().count(),
                "builds24h": (
                    Build.query.unrestricted_unsafe()
                    .filter(Build.date_created > timezone.now() - timedelta(days=1))
                    .count()
                ),
                "reposTotal": Repository.query.unrestricted_unsafe().count(),
                "usersTotal": User.query.count(),
            },
        }
