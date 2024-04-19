import pytest

from crawlers_tax_policy_data.spider.neimenggu import NMG_Spider
from crawlers_tax_policy_data.utils.log import init_log


@pytest.mark.asyncio
async def test_get_seeds_by_page():
    init_log()
    spider = NMG_Spider()
    await spider.post_all_list(start_public_date='20240301', end_public_date='20240419')

