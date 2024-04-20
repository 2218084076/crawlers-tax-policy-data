"""
http://hunan.chinatax.gov.cn/cs/lists/20190719067982
"""
from crawlers_tax_policy_data.tax_spider.base import TaxSpider


class ChangShaSpider(TaxSpider):
    """
    changsha spider
    """
    list_class_name = "newsList"

    @property
    def url(self):
        return 'http://hunan.chinatax.gov.cn/cs/lists/20190719067982'

    @property
    def headers(self):
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'hunan.chinatax.gov.cn',
            'Referer': 'http://hunan.chinatax.gov.cn/cs/lists/20190719067982',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }

    # async def get_list(self):
    #     """
    #     get list
    #     :return:
    #     """
    #     repo = await self.async_get_req(
    #         url=self.url,
    #         headers=self.headers
    # )
    # self.logger.info('%s GET %s', self.url, repo)
    # self.parser_list(repo)
    def get_list(self, start_date: str, end_date: str):
        """
        get list data

        TODO: 解析列表页数据，将每个详情页链接进行缓存，后续遍历采集
        :param start_date:
        :param end_date:
        :return:
        """
        self.sync_init_page()
        self.page.goto(self.url)
        all_news = self.page.locator(f'//*[@class="{self.list_class_name}"]').all()[0].locator('//a').all()
        for news in all_news:
            info = news.get_attribute('href')
            link = news.all_inner_texts()
            if info.split('\n')[-1] == start_date:
                self.parser_list(news)

    def parser_list(self, obj):
        """
        parser list page

        详情页链接结构 http://hunan.chinatax.gov.cn/cs/show/20240407548656
        :param obj:
        :return:
        """

    def parser(self, response):
        """
        Parser
        :param response:
        :return:
        """
