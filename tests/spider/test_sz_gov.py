import pytest

from crawlers_tax_policy_data.spider.sz_gov import SZGovSpider


@pytest.mark.asyncio
async def test_get_list():
    spider = SZGovSpider()
    await spider.get_list('20240418', '20240419')
