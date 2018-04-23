from io import BytesIO

from zeus.artifacts.webpack import WebpackStatsHandler
from zeus.models import Bundle


def test_result_generation(sample_webpack_stats, default_job):
    fp = BytesIO(sample_webpack_stats.encode("utf8"))

    handler = WebpackStatsHandler(default_job)
    handler.process(fp)

    results = list(
        Bundle.query.unrestricted_unsafe().filter(
            Bundle.job_id == default_job.id
        ).order_by(
            Bundle.name.asc()
        )
    )

    assert len(results) == 3

    r1 = results[0]
    assert r1.name == "app"
    asset_list = list(r1.assets)
    assert len(asset_list) == 1
    assert asset_list[0].name == "js/app.5bdbbccf.js"
    assert asset_list[0].size == 1100428
