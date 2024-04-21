from crawlers_tax_policy_data.spider.gov import GovSpider
from crawlers_tax_policy_data.utils.log import init_log


def test_get_list():
    init_log()
    spider = GovSpider()
    spider.get_news('20240412')
