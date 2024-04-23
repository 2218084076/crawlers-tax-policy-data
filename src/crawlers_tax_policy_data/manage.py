import asyncio

from crawlers_tax_policy_data.spider.gov import GovSpider
from crawlers_tax_policy_data.spider.shanghai_gov import ShangHaiGovSpider
from crawlers_tax_policy_data.spider.shenzhen import ShenZhengSpider


def crawlers_factory(city):
    """
    Factory method to create the corresponding crawlers instance based on the passed string
    :param city:
    :return:
    """
    crawlers = {
        "gov": GovSpider,
        'sz-gov': ShenZhengSpider,
        'shanghai-gov': ShangHaiGovSpider
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
