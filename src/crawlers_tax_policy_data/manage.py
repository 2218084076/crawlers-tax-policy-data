import asyncio

from crawlers_tax_policy_data.spider.gd_gov_doc_lib import GdGovDocLibSpider
from crawlers_tax_policy_data.spider.gd_gov_latest_policy import \
    GdGovLatestPolicySpider
from crawlers_tax_policy_data.spider.gov import GovSpider
from crawlers_tax_policy_data.spider.gz_gov import GzGovSpider
from crawlers_tax_policy_data.spider.shanghai_gov import ShangHaiGovSpider
from crawlers_tax_policy_data.spider.shenzhen import ShenZhengSpider
from crawlers_tax_policy_data.spider.zhejiang_gov import ZJSpider


def crawlers_factory(city):
    """
    Factory method to create the corresponding crawlers instance based on the passed string
    :param city:
    :return:
    """
    crawlers = {
        "gov": GovSpider,
        'sz-gov': ShenZhengSpider,
        'sh-gov': ShangHaiGovSpider,
        'zj-gov': ZJSpider,
        'gd-gov-latest-policy': GdGovLatestPolicySpider,
        'gd-gov-doc-lib': GdGovDocLibSpider,
        'gz-gov': GzGovSpider
    }
    return crawlers.get(city, lambda: None)()


async def all_crawlers():
    """
    Asynchronously run all defined crawler instances.
    """
    # Create a list of all crawler instances
    crawler_instances = [crawlers_factory(name) for name in ["gov", "sz-gov"]]

    # Use asyncio.gather to execute the run methods of all crawlers concurrently
    await asyncio.gather(*(crawler.run() for crawler in crawler_instances if crawler))
