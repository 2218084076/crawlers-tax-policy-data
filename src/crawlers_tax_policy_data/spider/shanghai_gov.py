import asyncio
import re
from datetime import datetime
from pathlib import Path

from lxml import etree

from crawlers_tax_policy_data.config import settings
from crawlers_tax_policy_data.spider.base import BaseSpider
from crawlers_tax_policy_data.storage.local import save_data
from crawlers_tax_policy_data.utils.utils import clean_text


class ShangHaiGovSpider(BaseSpider):
    """shanghai gov Spider"""
    folder = 'shanghai.gov.cn'

    @property
    def url(self):
        """
        url
        :return:
        """
        return 'https://www.shanghai.gov.cn/nw12344/index.html'

    @property
    def headers(self):
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": "Path=/; Path=/; zh_choose=s; _pk_testcookie.52.d738=1; _pk_id.52.d738=07cc14c1a9f284e4.1713850679.1.1713852410.1713850679.",
            "Host": "www.shanghai.gov.cn",
            "If-Modified-Since": "Tue, 23 Apr 2024 03:27:46 GMT",
            "If-None-Match": "W/\"66272ab2-268c\"",
            "Referer": "https://www.shanghai.gov.cn/nw12344/index.html",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
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
        start_date, end_date = self.check_date
        self.logger.info('Start collecting %s %s-%s data',
                         '上海市人民政府 https://www.shanghai.gov.cn/nw12344/index.html', start_date, end_date)
        await self.init_page()
        await self.page.goto(self.url)
        await self.page.wait_for_timeout(350)
        self.logger.info('get %s', self.page)
        detail_pages = await self.parse_news_list(start_date=start_date, end_date=end_date)

        if not detail_pages:
            self.logger.warning('上海市人民政府 <%s> no data', (start_date, end_date))
            return ''

        for _p in detail_pages:
            _link = _p.get('link')
            await self.init_page()
            await self.page.goto(url=_link)
            await self.page.wait_for_timeout(350)

            html_text = await self.page.content()
            detail_data = self.parse_detail_page(html_text)

            _title = re.sub(r'\s+', '', detail_data["title"])
            detail_page_html_file = Path(
                settings.GOV_OUTPUT_PAHT
            ) / self.folder / f'{start_date}-{end_date}' / f'''{_p['date']}-{_title}.html'''
            self.save_html(
                html_content=html_text,
                file=detail_page_html_file
            )

            detail_data.update({
                'link': _link,
                'date': _p['date'],
                'html_file': str(detail_page_html_file)
            })

            save_data(
                content=detail_data,
                file_path=Path(
                    settings.GOV_OUTPUT_PAHT) / self.folder / f'{start_date}-{end_date}' / f'{start_date}-{end_date}-public'
                                                                                           f'-information.csv'
            )
            await asyncio.sleep(0.3)

        await self.stop_page()

    async def parse_news_list(self, start_date: str, end_date: str):
        """
        parse news list
        :param start_date:
        :param end_date:
        :return:
        """
        res = []
        html_text = await self.page.content()
        html = etree.HTML(html_text, etree.HTMLParser(encoding="utf-8"))

        def parse_news_items(all_li: list):
            """
            parse news items
            :param all_li:
            :return:
            """
            for li in all_li:
                _page_date = ''.join(li.xpath('./span/text()'))
                _date = datetime.strptime(
                    _page_date,
                    '%Y-%m-%d'
                ).date()
                if (datetime.strptime(start_date, '%Y-%m-%d').date()
                        <= _date
                        <= datetime.strptime(end_date, '%Y-%m-%d').date()):
                    _title = ''.join(li.xpath('./a/text()'))
                    _link = f'https://www.shanghai.gov.cn{"".join(li.xpath("./a[1]/@href"))}'
                    res.append({'title': _title, 'link': _link, 'date': _page_date})

        items_list = html.xpath('//ul[@class="tadaty-list uli14 nowrapli list-date"]//li')
        parse_news_items(items_list)

        last_item_date_str = ''.join(items_list[-1].xpath('./span/text()'))
        last_item_date = datetime.strptime(last_item_date_str, '%Y-%m-%d').date()

        while last_item_date >= datetime.strptime(start_date, '%Y-%m-%d').date():
            await self.page.locator('//div[@name="whj_nextPage"]').click()
            await self.page.wait_for_timeout(350)
            page_text = await self.page.content()
            next_html = etree.HTML(page_text, etree.HTMLParser(encoding="utf-8"))
            next_items_list = next_html.xpath('//ul[@class="tadaty-list uli14 nowrapli list-date"]//li')
            parse_news_items(next_items_list)

            last_item_date_str = ''.join(next_items_list[-1].xpath('./span/text()'))
            last_item_date = datetime.strptime(last_item_date_str, '%Y-%m-%d').date()

        await self.stop_page()
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
