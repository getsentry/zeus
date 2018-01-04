import json

from zeus.config import db
from zeus.models import WebpackAsset, WebpackEntrypoint

from .base import ArtifactHandler


class WebpackStatsHandler(ArtifactHandler):
    supported_types = frozenset(
        ['application/webpack-stats+json'])

    def process(self, fp):
        job = self.job
        data = json.load(fp)
        for entrypoint_name, entrypoint in data['entrypoints'].items():
            db.session.add(WebpackEntrypoint(
                job=job,
                repository_id=job.repository_id,
                name=entrypoint_name,
                asset_names=entrypoint['assets'],
            ))

        for asset in data['assets']:
            db.session.add(WebpackAsset(
                job=job,
                repository_id=job.repository_id,
                filename=asset['name'],
                size=asset['size'],
                chunk_names=asset['chunkNames'],
            ))
        db.session.flush()
