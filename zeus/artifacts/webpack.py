import json

from collections import deque

from zeus.config import db
from zeus.models import Bundle, BundleAsset

from .base import ArtifactHandler


class WebpackStatsHandler(ArtifactHandler):
    supported_types = frozenset(
        ["application/x-webpack-stats+json", "application/webpack-stats+json"]
    )

    def process(self, fp):
        job = self.job
        data = json.load(fp)

        # XXX(dcramer): I'm guessing at how 'children' works here since its not documented
        # and I can't be asked to read the source
        children = deque([data])
        while children:
            child = children.pop()
            asset_index = {}
            for asset in child.get("assets", ()):
                asset_index[asset["name"]] = asset

            for bundle_name, asset_list in child.get("assetsByChunkName", {}).items():
                with db.session.begin_nested():
                    Bundle.query.unrestricted_unsafe().filter(
                        Bundle.job_id == job.id, Bundle.name == bundle_name
                    ).delete()
                    bundle_inst = Bundle(
                        job=job, repository_id=job.repository_id, name=bundle_name
                    )
                    db.session.add(bundle_inst)

                    complete = set()
                    for asset_name in asset_list:
                        # skip non-js assets like .css files
                        if asset_index.get(asset_name) is None:
                            continue
                        # dont track sourcemaps
                        if asset_name.endswith(".map"):
                            continue
                        # webpack can have duplicate asset names in the list
                        if asset_name in complete:
                            continue
                        complete.add(asset_name)

                        asset = asset_index[asset_name]
                        db.session.add(
                            BundleAsset(
                                job=job,
                                repository_id=job.repository_id,
                                bundle=bundle_inst,
                                name=asset["name"],
                                size=asset["size"],
                            )
                        )

            children.extend(child.get("children", ()))
            db.session.flush()
