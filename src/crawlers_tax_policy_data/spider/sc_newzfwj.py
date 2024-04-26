from crawlers_tax_policy_data.spider.base import BaseSpider


class ScNewzfwj(BaseSpider):
    """
    四川省人民政府 省政府政策文件 spider
    """
    folder = 'sc.gov.cn/省政府政策文件'

    async def collector(self, url: str, spider_name: str):
        """
        collector
        :param spider_name:
        :param url:
        :return:
        """
        start_date, end_date = self.check_date

        repo = await self.async_get_req(
            url=url,
            headers=self.headers
        )
        repo.encoding = 'utf-8'
        html_text = repo.text
