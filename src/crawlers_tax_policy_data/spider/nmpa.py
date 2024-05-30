"""
国家药监局
https://www.nmpa.gov.cn/xxgk/fgwj/gzwj/index.html  工作文件
https://www.nmpa.gov.cn/xxgk/fgwj/xzhgfxwj/index.html  行政规范性文件
"""
import asyncio
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from lxml import etree
from lxml.etree import _Element

from crawlers_tax_policy_data.config import settings
from crawlers_tax_policy_data.spider.base import BaseSpider
from crawlers_tax_policy_data.storage.local import save_data

pattern = r"[\u4e00-\u9fa5]+〔\d{4}〕\d+号"

crawlers_categories = [
    {
        'name': '工作文件',
        'url': 'https://www.nmpa.gov.cn/xxgk/fgwj/gzwj/index.html',
    },
    {
        'name': '行政规范性文件',
        'url': 'https://www.nmpa.gov.cn/xxgk/fgwj/xzhgfxwj/index.html',
    },
]


class NmpaSpider(BaseSpider):
    """
    国家药监局 spider
    """
    folder = '国家药监局'

    def __init__(self):
        super().__init__()
        self.start_date, self.end_date = self.check_date
        self.output_dir = Path(
            settings.GOV_OUTPUT_PAHT
        ) / self.folder / f'{self.start_date}-{self.end_date}'.replace('/', '')
        self.timestamp_format = '%Y-%m-%d'

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

    async def get_public_info(self, crawlers: dict):
        """
        get public info
        :param crawlers:
        :return:
        """
        _url = crawlers['url']
        self.logger.info(
            'Start collecting 国家药监局 %s %s %s--%s data',
            crawlers['name'], _url, self.start_date, self.end_date
        )

        await self.init_page()
        await self.page.goto(_url)
        await self.page.wait_for_timeout(500)
        await asyncio.sleep(0.5)

        detail_page_li = await self.list_page_parser(crawlers)

        if not detail_page_li:
            self.logger.warning(
                'No data found for 国家药监局 %s %s for dates %s--%s', crawlers['name'], _url, self.start_date,
                self.end_date
            )

        for pg in detail_page_li:
            await self.details_pg_processor(pg_data=pg, crawlers=crawlers)

    async def list_page_parser(self, crawlers: dict):
        """
        list pages parser
        :param crawlers:
        :return:
        """
        res = []
        _url = crawlers['url']
        html_text = await self.page.content()
        html: _Element = etree.HTML(
            html_text,
            etree.HTMLParser(encoding="utf-8")
        )

        li_list: List[_Element] = html.xpath(
            '//div[@class="list"]//li'
        )
        res.extend(self.per_line_parser(li_list))
        if not li_list:
            self.logger.warning(
                'No data found for 国家药监局 %s %s for dates %s--%s, retry', crawlers['name'], _url, self.start_date,
                self.end_date
            )
            await self.page.reload()
            await self.page.wait_for_timeout(500)

        last_pg_date_str = re.sub(r'[()]', '', ''.join(li_list[-1].xpath('.//span/text()'))).strip()
        last_pg_date = datetime.strptime(last_pg_date_str, self.timestamp_format).date()

        while last_pg_date >= datetime.strptime(self.start_date, self.timestamp_format).date():
            self.logger.info('Next pages, click next')
            await self.page.locator('//a[@target="_self" and text()="下一页"]').click()
            await self.page.wait_for_timeout(350)
            await asyncio.sleep(0.3)
            next_pg_text = await self.page.content()

            next_html: _Element = etree.HTML(
                next_pg_text,
                etree.HTMLParser(encoding="utf-8", remove_comments=False)
            )
            nex_li_list: List[_Element] = next_html.xpath(
                '//div[@class="list"]//li'
            )
            res.extend(self.per_line_parser(nex_li_list))

            _last_pg_date_str = re.sub(r'[()]', '', ''.join(nex_li_list[-1].xpath('.//span/text()'))).strip()
            last_pg_date = datetime.strptime(_last_pg_date_str, self.timestamp_format).date()

        self.logger.info('There are %s proclamation items', len(res))
        return res

    async def details_pg_processor(self, pg_data: dict, crawlers: dict):
        """
        Detail page processor

        :param crawlers:
        :param pg_data:
        :return:
        """
        _link = pg_data['link']

        if '.pdf' in _link:
            pg_content = {key: pg_data[key] for key in ['link', 'date', 'title']}

        else:
            await self.page.goto(_link)
            await self.page.wait_for_timeout(350)
            await asyncio.sleep(0.3)
            html_text = await self.page.content()
            self.logger.info('Detail page start collecting %s', _link)

            pg_content = self.details_pg_parser(html_text=html_text, pg_data=pg_data)

            _title = re.sub(r'\s+', '', pg_data["title"])
            detail_page_html_file = (
                    self.output_dir /
                    crawlers['name'] /
                    f'''{pg_data['date']}{_title}.html'''.replace('/', '')
            )
            self.save_html(
                html_content=html_text,
                file=detail_page_html_file
            )

            pg_content.update({key: pg_data[key] for key in ['link']})
            pg_content.update({'html_file': str(detail_page_html_file)})

        save_data(
            content=pg_content,
            file_path=(
                    self.output_dir / crawlers['name'] /
                    f"{self.start_date}/{self.end_date}-public-information.csv".replace('/', '-')
            )
        )
        await asyncio.sleep(0.5)

    def details_pg_parser(
            self,
            html_text: str,
            pg_data: dict
    ):
        """
        details page parser
        :param pg_data:
        :param html_text:
        :return:
        """
        _url_prefix = '/'.join(pg_data['link'].split('/')[:-1])

        file_xpath = self.build_file_xpath()
        xpath_query = f'//a[{file_xpath}]'

        html = etree.HTML(
            html_text,
            etree.HTMLParser(encoding="utf-8")  # fix garbled characters in requests
        )
        title = ''.join(html.xpath('//meta[@name="ArticleTitle"]/@content')).strip()
        # parse top information
        _top_item_tit = ''
        _top_item_con = ''
        top_info_lis = []
        for index, td in enumerate(html.xpath('//div[@class="wenzhang-table"]//td')):
            _txt = ''.join(td.xpath('.//text()')).strip()
            if index % 2:
                _top_item_con = _txt.replace('\n', '').replace('\t', '')
            if not index % 2:
                _top_item_tit = _txt
            elif _top_item_tit and _top_item_con:
                top_info_lis.append(f'''{_top_item_tit}: {_top_item_con}''')
                _top_item_tit = ''
                _top_item_con = ''
        top_info = '\n'.join(top_info_lis)
        # text title
        text_tit = ''.join(html.xpath(
            '//div[@class="wenzhang w1200-auto"]//h2[@class="title"]//text() | //div[@class="wenzhang w1200-auto"]//h3[@class="two-title"]//text()'))
        texts = html.xpath('//div[@class="wenzhang w1200-auto"]/div[@class="text"]//p//text()')

        all_related_links = []

        all_appendix = []
        for i in html.xpath(xpath_query):
            _filename = ''.join(i.xpath('.//text()'))
            _file_link = ''.join(i.xpath('.//@href')).strip()
            all_appendix.append(
                f'''
                {_filename}  {'/'.join(self.page.url.split('/')[:3])}{_file_link}
            '''.strip()
            )
        editor = ''.join(html.xpath('//h3[@class="two-title"]/text()')).strip()
        if not editor:
            editor = ''.join(re.findall(r"\d{4}年第\d+号", title))

        return {
            'text': f'''{top_info}\n\n{text_tit.strip()}\n\n{''.join(texts)}''',
            'appendix': ',\n'.join(all_appendix).replace('\xa0', ''),
            'related_documents': ',\n'.join(all_related_links),
            'title': title,
            'editor': editor,
            'date': ''.join(html.xpath('//meta[@name="PubDate"]/@content')).strip()
        }

    def per_line_parser(
            self,
            li_list_html: List[_Element]
    ) -> List[Dict[str, str]]:
        """
        Per-line parser

        使用 `-` 格式日期
        :param li_list_html:
        :return:
        """
        res = []
        for line in li_list_html:
            _page_date = re.sub(r'[()]', '', ''.join(line.xpath('.//span/text()'))).strip()
            if not _page_date:
                continue
            try:
                _date = datetime.strptime(
                    _page_date,
                    self.timestamp_format
                ).date()
            except ValueError:
                continue
            if (datetime.strptime(self.start_date, self.timestamp_format).date()
                    <= _date
                    <= datetime.strptime(self.end_date, self.timestamp_format).date()):
                _title = ''.join(line.xpath('.//a/text()')).strip()
                _url_prefix = '/'.join(self.page.url.split('/')[:3])
                detail_page_link = ''.join(line.xpath('.//a/@href')).strip()
                _link = detail_page_link.replace('../../..', _url_prefix)
                res.append({
                    'title': _title,
                    'link': _link,
                    'date': _page_date,
                })
        return res

    async def run(self):
        """
        run crawlers
        :return:
        """
        self.logger.info('start running crawlers...')
        for _s in crawlers_categories:
            await self.get_public_info(_s)
            await self.stop_page()
