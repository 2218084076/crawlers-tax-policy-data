from crawlers_tax_policy_data.spider.gov import GovSpider


def crawlers_factory(city):
    """
    Factory method to create the corresponding crawlers instance based on the passed string
    :param city:
    :return:
    """
    crawlers = {
        "gov": GovSpider,
    }
    return crawlers.get(city, lambda: None)()
