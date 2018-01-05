import json

from zeus.config import db
from zeus.models import BundleAsset, BundleEntrypoint

from .base import ArtifactHandler


class WebpackStatsHandler(ArtifactHandler):
    supported_types = frozenset(
        ['application/webpack-stats+json'])

    def process(self, fp):
        job = self.job
        data = json.load(fp)

        asset_cache = {}
        for asset in data['assets']:
            asset_inst = BundleAsset(
                job=job,
                repository_id=job.repository_id,
                name=asset['name'],
                size=asset['size'],
                chunk_names=asset['chunkNames'],
            )
            db.session.add(asset_inst)
            asset_cache[asset['name']] = asset_inst

        for entrypoint_name, entrypoint in data['entrypoints'].items():
            entrypoint_inst = BundleEntrypoint(
                job=job,
                repository_id=job.repository_id,
                name=entrypoint_name,
            )
            for asset_name in entrypoint['assets']:
                entrypoint_inst.assets.append(asset_cache[asset_name])
            db.session.add(entrypoint_inst)

        db.session.flush()
