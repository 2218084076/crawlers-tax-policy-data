"""
国家外汇管理局
https://www.safe.gov.cn/safe/zcfg/index.html
"""
import re
from datetime import datetime
from pathlib import Path
from typing import List

from lxml import etree

from crawlers_tax_policy_data.config import settings
from crawlers_tax_policy_data.spider.base import BaseSpider
from crawlers_tax_policy_data.utils.utils import clean_text


class SafeSpider(BaseSpider):
    """
    国家外汇管理局 spider
    """
    folder = 'safe.gov.cn'

    def __init__(self):
        super().__init__()
        self.start_date, self.end_date = self.check_date
        self.output_dir = Path(
            settings.GOV_OUTPUT_PAHT
        ) / self.folder / f'{self.start_date}-{self.end_date}'

    @property
    def url(self):
        """
        url
        :return:
        """
        return 'https://www.safe.gov.cn/safe/zcfg/index.html'

    @property
    def headers(self):
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                      "*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": "gotopc=false; __utrace=d25d740daa0ad5112aeee3ea57d97d85",
            "Host": "www.safe.gov.cn",
            "If-Modified-Since": "Fri, 26 Apr 2024 17:13:49 GMT",
            "If-None-Match": "\"662be0cd-670c\"",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/124.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Chromium\";v=\"124\", \"Google Chrome\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
        }

    @property
    def check_date(self) -> tuple:
        """
        check date
        :return:
        """
        check_date = self.date
        if isinstance(check_date, dict):
            start_date = f'{check_date["start"].year}-{int(check_date["start"].month):02d}-{int(check_date["start"].day):02d}'
            end_date = f'{check_date["end"].year}-{int(check_date["end"].month):02d}-{int(check_date["end"].day):02d}'
        else:
            start_date = f'{check_date.year}-{int(check_date.month):02d}-{int(check_date.day):02d}'
            end_date = f'{check_date.year}-{int(check_date.month):02d}-{int(check_date.day):02d}'
        return start_date, end_date

    async def get_public_info(self):
        """
        get public information
        :return:
        """
        self.logger.info(
            'Start collecting 国家外汇管理局 %s %s-%s data',
            self.url, self.start_date, self.end_date
        )
        await self.init_page()
        await self.page.goto(self.url)
        await self.page.wait_for_timeout(350)
        html_text = await self.page.content()
        self.logger.info('get %s', self.page)

        detail_page_li = await self.list_page_parser(html_text)

    async def list_page_parser(self, html_text: str):
        """
        parse news list
        :param html_text:
        :return:
        """
        res = []
        html_text = await self.page.content()
        html = etree.HTML(html_text, etree.HTMLParser(encoding="utf-8"))

        li_list: List[etree._Element] = html.xpath('//div[@class="list_conr"]//li')
        return res

    def per_line_parser(self, li_list_html: List[etree._Element]):
        """
        Per-line parser

        使用 `-` 格式日期
        :param li_list_html:
        :return:
        """
        res = []
        prefix = 'https://www.sc.gov.cn'
        for line in li_list_html:
            _page_date = ''.join(line.xpath('.//div[@class="lie5"]//text()')).strip()
            _date = datetime.strptime(
                _page_date,
                '%Y-%m-%d'
            ).date()
            if (datetime.strptime(self.start_date, '%Y-%m-%d').date()
                    <= _date
                    <= datetime.strptime(self.end_date, '%Y-%m-%d').date()):
                _title = ''.join(line.xpath('.//div[@class="lie2"]//text()')).strip()
                _link = f'''{prefix}{''.join(line.xpath('.//div[@class="lie2"]/a/@href')).strip()}'''
                _editor = ''.join(line.xpath('.//div[@class="lie3"]//text()')).strip()

                res.append({
                    'title': _title,
                    'link': _link,
                    'date': _page_date,
                    'editor': _editor,
                })

        return res

    def parse_detail_page(self, html_text: str):
        """
        parse detail page
        :param html_text:
        :return:
        """
        res = {}
        self.logger.info('parse detail_page text data')

        file_xpath = self.build_file_xpath()
        xpath_query = f'//a[{file_xpath}]'

        html = etree.HTML(html_text, etree.HTMLParser(encoding="utf-8"))  # fix garbled characters in requests
        title = re.sub(r'\s+', '', clean_text(''.join(html.xpath('//div[@id="ivs_title"]/text()'))))
        # 文号
        editor = clean_text(''.join(html.xpath('//div[@id="ivs_content"]/p[2]/text()'))) if self.is_match(
            ''.join(html.xpath('//div[@id="ivs_content"]/p[2]/text()'))) else ''

        related_documents = ',\n'.join(
            [' - '.join(
                (''.join(item.xpath('./a/@title')), 'https://www.shanghai.gov.cn' + ''.join(item.xpath('./a/@href'))))
                for item in
                html.xpath('//div[@class="newsbox"]/ul//li')]
        )
        # 附件
        all_appendix = self.extract_links(html, xpath_query)
        res.update({
            'title': title,
            'text': title + clean_text(''.join(html.xpath('//div[@id="xggj"]//text()'))),
            'editor': editor,
            'appendix': ',\n'.join(all_appendix).replace('\xa0', ''),
            'related_documents': related_documents,
        })

        return res

    async def run(self):
        """
        run crawlers
        :return:
        """
        self.logger.info('start running crawlers...')
        await self.get_public_info()

    @staticmethod
    def extract_links(html, xpath):
        """
        Extract the links according to the given XPath
        :param html:
        :param xpath:
        :return:
        """
        res = [''.join(link.xpath('./text()')).strip() + ' https://www.shanghai.gov.cn' + ''.join(
            link.xpath('@href')).strip() for link
               in html.xpath(xpath)]
        return list(set(res))
