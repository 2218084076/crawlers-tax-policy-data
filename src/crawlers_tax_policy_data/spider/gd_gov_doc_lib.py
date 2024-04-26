"""
广东省人民政府
` 文件库 > 全部文件 ` 数据采集
http://www.gd.gov.cn/zwgk/wjk/qbwj/
"""
import asyncio
import re
from datetime import datetime
from pathlib import Path

from lxml import etree

from crawlers_tax_policy_data.config import settings
from crawlers_tax_policy_data.spider.base import BaseSpider
from crawlers_tax_policy_data.storage.local import save_data
from crawlers_tax_policy_data.utils.utils import clean_text


class GdGovDocLibSpider(BaseSpider):
    """
    广东省人民政府 `  文件库 > 全部文件 ` 数据采集
    """
    folder = 'gd.gov.cn'

    @property
    def url(self):
        """
        url
        :return:
        """
        return 'http://www.gd.gov.cn/zwgk/wjk/qbwj/'
        # next page http://www.gd.gov.cn/zwgk/wjk/qbwj/index_2.html

    @property
    def headers(self):
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": "front_uc_session=eyJpdiI6IkRBY09IZDF3aVRZeHQyNEFtRiswQmc9PSIsInZhbHVlIjoiT2xVUjZYVGdYcGhwNVRjdzkyT3BcL3VkWWJPNkNza1Q2OWQwTjM5NnZ1akFtUHkxOEU2Zk40Q1dzaHJ0YjFNQ1wvIiwibWFjIjoiODA0ZGI4MDU4YzVhMmE5Mzg3MDBiOGFkMGFmZTg0NzUwMzUxMjUzYjMxY2UzZDYwMGQwNmNkMjQ0YTMzZDE3YiJ9",
            "Host": "www.gd.gov.cn",
            "Referer": "http://www.gd.gov.cn/",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
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
        self.logger.info('Start collecting `%s` <%s> data', '广东省人民政府 > 文件库', (start_date, end_date))
        detail_pages = await self.parse_news_list(start_date=start_date, end_date=end_date)

        if not detail_pages:
            self.logger.warning('广东省人民政府 > 文件库  <%s> no data', (start_date, end_date))
            return ''

        for _p in detail_pages:
            _link = _p.get('link')
            if 'pdf' in _link:
                save_data(
                    content={'link': _link, 'date': _p['date'], 'title': _p['title'], 'editor': _p['editor']},
                    file_path=Path(
                        settings.GOV_OUTPUT_PAHT
                    ) / self.folder / f'{start_date}-{end_date}' / 'document library' / f'{start_date}-{end_date}-public'
                                                                                        f'-information.csv')
            else:
                _repo = await self.async_get_req(
                    url=_link,
                    headers=self.headers
                )
                _repo.encoding = 'utf-8'
                html_text = _repo.text
                detail_data = self.parse_detail_page(html_text)

                _title = re.sub(r'\s+', '', detail_data["title"])
                detail_page_html_file = Path(
                    settings.GOV_OUTPUT_PAHT
                ) / self.folder / f'{start_date}-{end_date}' / 'document library' / f'''{_p['date']}-{_title}.html'''
                self.save_html(
                    html_content=html_text,
                    file=detail_page_html_file
                )

                detail_data.update({
                    'link': _link,
                    'date': _p['date'],
                    'editor': _p['editor'],
                    'html_file': str(detail_page_html_file)
                })

                save_data(
                    content=detail_data,
                    file_path=Path(
                        settings.GOV_OUTPUT_PAHT) / self.folder / f'{start_date}-{end_date}' / 'document library' / f'{start_date}-{end_date}-public'
                                                                                                                    f'-information.csv'
                )
                await asyncio.sleep(0.3)

    async def parse_news_list(self, start_date: str, end_date: str):
        """
        parse news list
        :param start_date:
        :param end_date:
        :return:
        """
        res = []
        repo = await self.async_get_req(
            url=self.url,
            headers=self.headers,
        )
        repo.encoding = 'utf8'
        html = etree.HTML(repo.text, etree.HTMLParser(encoding="utf-8"))

        def parse_news_items(all_row: list):
            """
            parse news items
            :param all_row:
            :return:
            """
            for row in all_row:
                _page_date = clean_text(''.join(row.xpath('./span[@class="date"]/text()')))
                _date = datetime.strptime(
                    _page_date,
                    '%Y-%m-%d'
                ).date()
                if (datetime.strptime(start_date, '%Y-%m-%d').date()
                        <= _date
                        <= datetime.strptime(end_date, '%Y-%m-%d').date()
                ):
                    _title = clean_text(''.join(row.xpath('./span[@class="name"]/a/text()')))
                    _link = clean_text(''.join(row.xpath('./span/a/@href')))
                    _editor = clean_text(''.join(row.xpath('./span[@class="wh"]/text()')))
                    res.append({'title': _title, 'link': _link, 'date': _page_date, 'editor': _editor})

        li_list = html.xpath('//div[@class="viewList"]/ul//li')
        parse_news_items(li_list)

        last_item_date_str = clean_text(''.join(li_list[-1].xpath('./span[@class="date"]/text()')))
        last_item_date = datetime.strptime(last_item_date_str, '%Y-%m-%d').date()
        _p_num = 2
        while last_item_date >= datetime.strptime(start_date, '%Y-%m-%d').date():
            repo = await self.async_get_req(
                url=f'{self.url}index_{_p_num}.html',
                headers=self.headers,
            )
            repo.encoding = 'utf8'
            next_html = etree.HTML(repo.text, etree.HTMLParser(encoding="utf-8"))
            next_items_list = next_html.xpath('//div[@class="viewList"]/ul//li')
            parse_news_items(next_items_list)

            last_item_date_str = ''.join(next_items_list[-1].xpath('./span[@class="date"]/text()'))
            last_item_date = datetime.strptime(last_item_date_str, '%Y-%m-%d').date()
            _p_num += 1

        return res

    def parse_detail_page(self, html_text: str):
        """
        parse detail page
        :param html_text:
        :return:
        """
        res = {}
        file_xpath = self.build_file_xpath()
        xpath_query = f'//div[@class="zw"]//a[{file_xpath}]'

        html = etree.HTML(
            html_text,
            etree.HTMLParser(encoding="utf-8")  # fix garbled characters in requests
        )

        title = clean_text(''.join(html.xpath('//div[@class="introduce"]/div[@class="row"]//span/text()')))
        all_related_links = [''.join(i.xpath('./text()')) + '-' + ''.join(i.xpath('@href')) for i in
                             html.xpath('//div[@class="aside right"]//a')]
        texts = html.xpath('//div[@class="zw"]//text()')
        cleaned_texts = [clean_text(text) for text in texts]
        all_appendix = self.extract_links(html, xpath_query)

        res.update({
            'title': title,
            'text':  '\n'.join(cleaned_texts).strip(),
            'related_documents': ',\n'.join(all_related_links),
            'appendix': ',\n'.join(all_appendix).replace('\xa0', ''),
        })

        return res

    async def run(self):
        """
        run crawlers
        :return:
        """
        self.logger.info('start running crawlers...')
        await self.get_public_info()
