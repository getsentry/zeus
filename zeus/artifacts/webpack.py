import json

from zeus.config import db
from zeus.models import Bundle, BundleAsset

from .base import ArtifactHandler


class WebpackStatsHandler(ArtifactHandler):
    supported_types = frozenset(
        ['application/webpack-stats+json'])

    def process(self, fp):
        job = self.job
        data = json.load(fp)

        asset_index = {}
        for asset in data['assets']:
            asset_index[asset['name']] = asset

        for bundle_name, asset_list in data['assetsByChunkName'].items():
            bundle_inst = Bundle(
                job=job,
                repository_id=job.repository_id,
                name=bundle_name,
            )
            db.session.add(bundle_inst)
            for asset_name in asset_list:
                asset = asset_index[asset_name]
                db.session.add(BundleAsset(
                    job=job,
                    repository_id=job.repository_id,
                    bundle=bundle_inst,
                    name=asset['name'],
                    size=asset['size'],
                ))
        db.session.flush()
