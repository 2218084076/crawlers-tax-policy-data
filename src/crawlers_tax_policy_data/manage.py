import asyncio

from crawlers_tax_policy_data.spider.bj_gov import BjGovSpider
from crawlers_tax_policy_data.spider.cbirc import CbircSpider
from crawlers_tax_policy_data.spider.csrc import CsrcSpider
from crawlers_tax_policy_data.spider.gd_gov_doc_lib import GdGovDocLibSpider
from crawlers_tax_policy_data.spider.gd_gov_latest_policy import \
    GdGovLatestPolicySpider
from crawlers_tax_policy_data.spider.gov import GovSpider
from crawlers_tax_policy_data.spider.gz_gov import GzGovSpider
from crawlers_tax_policy_data.spider.js_gov import JsGovSpider
from crawlers_tax_policy_data.spider.miit import MiitSpider
from crawlers_tax_policy_data.spider.mof import MofSpider
from crawlers_tax_policy_data.spider.ndrc import NdrcSpider
from crawlers_tax_policy_data.spider.pbc import PbcSpider
from crawlers_tax_policy_data.spider.safe_gov import SafeSpider
from crawlers_tax_policy_data.spider.samr import SamrSpider
from crawlers_tax_policy_data.spider.sc_gov import ScGovSpider
from crawlers_tax_policy_data.spider.shanghai_gov import ShangHaiGovSpider
from crawlers_tax_policy_data.spider.shenzhen import ShenZhengSpider
from crawlers_tax_policy_data.spider.zhejiang_gov import ZJSpider

crawlers = {
    "gov": GovSpider,
    'sz-gov': ShenZhengSpider,
    'sh-gov': ShangHaiGovSpider,
    'zj-gov': ZJSpider,
    'gd-gov-latest-policy': GdGovLatestPolicySpider,
    'gd-gov-doc-lib': GdGovDocLibSpider,
    'gz-gov': GzGovSpider,
    'js-gov': JsGovSpider,
    'bj-gov': BjGovSpider,
    'sc-gov': ScGovSpider,  # `gfxwj` `newzfwj` `bmgfxwj` 三个网址的爬虫，请在 settings.yml 配置文件中 SC_GOV 参数确认
    'safe': SafeSpider,
    'mof': MofSpider,
    'csrc': CsrcSpider,
    'miit': MiitSpider,
    'pbc': PbcSpider,
    'ndrc': NdrcSpider,
    'cbirc': CbircSpider,
    'samr': SamrSpider
}


def crawlers_factory(city):
    """
    Factory method to create the corresponding crawlers instance based on the passed string
    :param city:
    :return:
    """
    return crawlers.get(city, lambda: None)()


async def all_crawlers():
    """
    Sequentially run all defined crawler instances.
    :return: 
    """""
    crawler_instances = [crawlers.get(name, lambda: None)() for name in crawlers.keys()]

    for crawler in crawler_instances:
        if crawler:
            await crawler.run()
            await asyncio.sleep(5)
