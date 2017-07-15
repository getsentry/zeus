from flask import request

from zeus.models import Build
from zeus.api import client

from .base import BaseHook


class BuildHook(BaseHook):
    def post(self, hook, build_xid):
        build = Build.query.filter(
            Build.organization_id == hook.organization_id,
            Build.project_id == hook.project_id,
            Build.provider == hook.provider,
            Build.external_id == build_xid,
        ).first()

        json = request.get_json() or {}
        json['external_id'] = build_xid
        json['provider'] = hook.provider

        if build:
            response = client.put(
                '/projects/{}/{}/builds/{}'.format(
                    hook.organization.name,
                    hook.project.name,
                    build.number,
                ),
                json=json
            )
        else:
            response = client.post(
                '/projects/{}/{}/builds'.format(
                    hook.organization.name,
                    hook.project.name,
                ),
                json=json
            )

        return response
