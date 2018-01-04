from io import BytesIO

from zeus.artifacts.webpack import WebpackStatsHandler
from zeus.models import WebpackAsset, WebpackEntrypoint


def test_result_generation(sample_webpack_stats, default_job):
    fp = BytesIO(sample_webpack_stats.encode('utf8'))

    handler = WebpackStatsHandler(default_job)
    handler.process(fp)

    results = list(WebpackEntrypoint.query.unrestricted_unsafe().filter(
        WebpackEntrypoint.job_id == default_job.id,
    ).order_by(WebpackEntrypoint.name.asc()))

    assert len(results) == 3

    r1 = results[0]
    assert r1.name == 'app'
    assert r1.asset_names == [
        'js/vendor.5bdbbccf.js',
        'js/vendor.5bdbbccf.js.map',
        'js/app.5bdbbccf.js',
        'js/app.5bdbbccf.js.map'
    ]

    results = list(WebpackAsset.query.unrestricted_unsafe().filter(
        WebpackAsset.job_id == default_job.id,
    ).order_by(WebpackAsset.filename.asc()))

    assert len(results) == 15

    r1 = results[0]
    assert r1.filename == 'asset-manifest.json'
    assert r1.size == 730
    assert r1.chunk_names == []

    r2 = results[1]
    assert r2.filename == 'js/0.5bdbbccf.chunk.js'
    assert r2.size == 31143
    assert r2.chunk_names == []
