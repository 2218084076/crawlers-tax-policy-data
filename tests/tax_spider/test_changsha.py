import pytest

from crawlers_tax_policy_data.tax_spider.changsha import ChangShaSpider


# @pytest.mark.asyncio
# async def test_get_list():
#     """
#     test get list
#     :return:
#     """
#     spider = ChangShaSpider()
#     await spider.get_list()
def test_get_list():
    """
    test get list
    :return:
    """
    spider = ChangShaSpider()
    spider.get_list()
