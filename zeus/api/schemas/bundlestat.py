from collections import defaultdict
from marshmallow import Schema, fields, pre_dump
from uuid import UUID

from zeus.config import db


class BundleAssetSchema(Schema):
    name = fields.Str(required=True)
    size = fields.Int()


class BundleEntrypointResultSchema(Schema):
    id = fields.UUID(dump_only=True)
    job_id = fields.UUID(dump_only=True)
    assets = fields.List(fields.Nested(BundleAssetSchema))


class AggregateBundleEntrypointSchema(Schema):
    name = fields.Str(required=True)
    results = fields.List(fields.Nested(
        BundleEntrypointResultSchema), required=True)

    @pre_dump(pass_many=True)
    def process_aggregates(self, data, many):
        from zeus.models import BundleAsset, bundle_entrypoint_asset

        if not many:
            item_list = [data]
        else:
            item_list = data

        entrypoint_ids = set()
        for item in item_list:
            entrypoint_ids.update((e[0] for e in item.results))

        assets_by_entrypoint = defaultdict(list)
        queryset = db.session.query(bundle_entrypoint_asset.c.entrypoint_id, BundleAsset).filter(
            bundle_entrypoint_asset.c.entrypoint_id.in_(entrypoint_ids),
            BundleAsset.id == bundle_entrypoint_asset.c.asset_id,
        )
        for entrypoint_id, asset in queryset:
            assets_by_entrypoint[entrypoint_id].append(asset)

        result = [{
            'name': item.name,
            'results': [{
                'id': UUID(e[0]),
                'job_id': UUID(e[1]),
                'assets': assets_by_entrypoint[UUID(e[0])],
            } for e in item.results],
        } for item in item_list]

        if many:
            return result
        return result[0]
