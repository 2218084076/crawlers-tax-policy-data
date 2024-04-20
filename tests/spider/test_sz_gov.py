from crawlers_tax_policy_data.spider.sz_gov import SZGovSpider


def test_get_list():
    spider = SZGovSpider()
    spider.get_list('20240418', '20240419')
