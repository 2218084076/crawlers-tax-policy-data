# encoding:utf-8
"""
上海市浦东新区人民政府
https://www.pudong.gov.cn/zwgk-search-front/api/pudong/authority

"""
import uuid

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

    @property
    def headers(self):
        """
        headers
        :return:
        """
        return {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Content-Length": "294",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://www.pudong.gov.cn",
            "Referer": "https://www.pudong.gov.cn/zwgk-search-front/api/pudong/authority",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua": "\"Chromium\";v=\"124\", \"Google Chrome\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
        }

    def get_news(self):
        """
        get news
        :return:
        """
        check_date = self.date
        if isinstance(check_date, dict):
            start_date = f'{check_date["start"].year}-{int(check_date["start"].month):02d}-{int(check_date["start"].day):02d}'
            end_date = f'{check_date["end"].year}-{int(check_date["end"].month):02d}-{int(check_date["end"].day):02d}'
        else:
            start_date = f'{check_date.year}-{int(check_date.month):02d}-{int(check_date.day):02d}'
            end_date = f'{check_date.year}-{int(check_date.month):02d}-{int(check_date.day):02d}'
        # post_data = {
        #     "FdSolrqt": f"{uuid.uuid4()}"
        # }
        repo = self.post_req(
            url=f'{self.url}?FdSolrqt=0Ti3U6GlqEJc5HQSs88SgXYsoo0qSujLL2vDmmOqVX_cYUQi0SHzIEcNDlat7v_NcuMgJAEOmFjTA_gdrpSC9Zyobc1t3gJgA',
            headers=self.headers,
            # json=post_data
        )
        self.logger.info(repo)

    def run(self):
        """
        run crawlers
        :return:
        """
        self.get_news()
