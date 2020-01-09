import pytest

from zeus.vcs.utils import get_vcs


@pytest.mark.asyncio
async def test_get_vcs(vcs_app, default_repo):
    vcs = await get_vcs(vcs_app, default_repo["id"])
    assert vcs.url == "https://github.com/getsentry/zeus.git"
