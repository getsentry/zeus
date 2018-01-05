from io import BytesIO

from zeus.artifacts.webpack import WebpackStatsHandler
from zeus.models import BundleAsset, BundleEntrypoint


def test_result_generation(sample_webpack_stats, default_job):
    fp = BytesIO(sample_webpack_stats.encode('utf8'))

    handler = WebpackStatsHandler(default_job)
    handler.process(fp)

    results = list(BundleEntrypoint.query.unrestricted_unsafe().filter(
        BundleEntrypoint.job_id == default_job.id,
    ).order_by(BundleEntrypoint.name.asc()))

    assert len(results) == 3

    r1 = results[0]
    assert r1.name == 'app'
    assert [a.name for a in r1.assets] == [
        'js/vendor.5bdbbccf.js',
        'js/vendor.5bdbbccf.js.map',
        'js/app.5bdbbccf.js',
        'js/app.5bdbbccf.js.map'
    ]

    results = list(BundleAsset.query.unrestricted_unsafe().filter(
        BundleAsset.job_id == default_job.id,
    ).order_by(BundleAsset.name.asc()))

    assert len(results) == 15

    r1 = results[0]
    assert r1.name == 'asset-manifest.json'
    assert r1.size == 730
    assert r1.chunk_names == []

    r2 = results[1]
    assert r2.name == 'js/0.5bdbbccf.chunk.js'
    assert r2.size == 31143
    assert r2.chunk_names == []
