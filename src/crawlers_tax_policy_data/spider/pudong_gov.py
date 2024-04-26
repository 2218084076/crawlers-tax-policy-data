# encoding:utf-8
"""
上海市浦东新区人民政府
https://www.pudong.gov.cn/zwgk-search-front/api/pudong/authority

"""

from crawlers_tax_policy_data.spider.base import BaseSpider


class PudongSpider(BaseSpider):
    """
    pudong spider
    """

    @property
    def url(self):
        """
        url
        :return:
        """
        return 'https://www.pudong.gov.cn/zwgk-search-front/api/pudong/search'
