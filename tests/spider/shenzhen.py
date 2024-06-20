import pytest

from crawlers_tax_policy_data.spider.shenzhen import ShenZhengSpider
from crawlers_tax_policy_data.utils.log import init_log


@pytest.mark.asyncio
async def test_run():
    init_log()
    spider = ShenZhengSpider()
    await spider.run()
