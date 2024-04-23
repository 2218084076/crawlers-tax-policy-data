# encoding:utf-8
"""
上海市浦东新区人民政府
https://www.pudong.gov.cn/zwgk-search-front/api/pudong/authority

"""
from crawlers_tax_policy_data.config import settings
from crawlers_tax_policy_data.spider.base import BaseSpider
from crawlers_tax_policy_data.utils.utils import date_obj


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
        return 'https://www.pudong.gov.cn/zwgk-search-front/api/pudong/authority'

    @property
    def headers(self):
        """
        headers
        :return:
        """
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": "JSESSIONID=0BF5150558368284AE7A720E97C4B457; 0zaLpREBxJs7S=60kqu64nJWEH3G.LotTED9NGHYyl9IOfGLy_5BE3m4HdzANgcN6Mj0UTO0gLb46NfmX3aAWmiJUo2eO1oktfl3hG; 0zaLpREBxJs7O=60ZBWgOmhiaieIh.NZidAyKC4SVmzVu.X.S64cpF2Pizuvn7joaCBjJ1xMdCIE6YeZsk9jDc2hQZ26UH6bvEvxfq; zh_choose=s; _pk_testcookie.300.0950=1; _pk_id.300.0950=935f9d970be1b4ab.1713795951.1.1713795951.1713795951.; _pk_ses.300.0950=1; 0zaLpREBxJs7T=02XqYo9ZlVsWWTr5jUAJ3HA3vaEV8dlpu939o.mwRRTlO_gCLYpRPZP6C4t5O6gFuIx.XnqyjrCPPwaNWmmjcoNnNaQOYFFXqz3RHWIsmtdCY344QN6_f0Z27pMOsnqGlzURhtJIK0uiq860QJ.vjhZAjnMcvccVo_pGo3e3qfZHojlYE3UChw..P08OxO1Rn8Wdm3suhBCMGOiN3fg5OKg_sL5vBHkBKwGn2aTTxW6tsA2QKjctOL3lX8h.a9ATJ9Mrq8Txja6yKcLhnaKgvO4tuNRGXt5a7ehZd1yf23gwFTxMcam1Zp1bE1f9ZyrYKMceKdshzYR1D9sasWntgma5YJjSIJ7p2UaW4iETRe4fF_mY3S9AnyWfBjmu.7ZL0Z3QnyjnAM8tJjjlr8eKIwctYQz_C1ibybH3I5bTAwz3",
            "Referer": "https://www.pudong.gov.cn/zwgk-search-front/api/pudong/authority",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"",
            "sec-ch-ua-mobile": "?0",
        }

    def get_news(self):
        """
        get news
        :return:
        """
        check_date = settings.CRAWLERS_DATE
        check_date_obj = date_obj(check_date)
        check_page_date = f'{check_date_obj.year}-{int(check_date_obj.month):02d}-{int(check_date_obj.day):02d}'
        self.sync_init_page()
        self.page.goto(self.url)
        self.logger.info(self.page)

    def run(self):
        """
        run crawlers
        :return:
        """
        self.get_news()
