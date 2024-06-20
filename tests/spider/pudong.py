from crawlers_tax_policy_data.spider.pudong_gov import PudongSpider
from crawlers_tax_policy_data.spider.shanghai_gov import ShangHaiGovSpider
from crawlers_tax_policy_data.utils.log import init_log


def test_run():
    init_log()
    spider = PudongSpider()
    spider.run()


def test_get():
    init_log()
    spider = PudongSpider()
    spider.get_req(
        url='https://www.shanghai.gov.cn/nw12344/index.html'
    )


def test_shanghai():
    init_log()
    spider = ShangHaiGovSpider()
    spider.run()
