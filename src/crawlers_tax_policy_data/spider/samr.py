"""
市场监督管理总局
https://www.samr.gov.cn/zw/zjwj/index.html
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
from crawlers_tax_policy_data.utils.utils import clean_text

pattern = r"[\u4e00-\u9fa5]+〔\d{4}〕\d+号"

crawlers_categories = {
    'asd': {
        'name': '行政规范性文件',
        'tag_xpath': '//span[@item="4215"]',
        'item_id': '4215'
    },
    'of': {
        'name': '其他文件',
        'tag_xpath': '//span[@item="4216"]',
        'item_id': '4216'
    },
}


class SamrSpider(BaseSpider):
    """
    市场监督管理总局 spider
    """
    folder = '市场监督管理总局'

    def __init__(self):
        super().__init__()
        self.start_date, self.end_date = self.check_date
        self.output_dir = Path(
            settings.GOV_OUTPUT_PAHT
        ) / self.folder / f'{self.start_date}-{self.end_date}'.replace('/', '')
        self.timestamp_format = '%Y-%m-%d'

    @property
    def url(self):
        """
        url
        :return:
        """
        return 'https://www.samr.gov.cn/zw/zjwj/index.html'

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
        get public info
        :return:
        """

        self.logger.info(
            'Start collecting 市场监督管理总局  %s %s--%s data',
            self.url, self.start_date, self.end_date
        )

        await self.init_page()
        await self.page.goto(self.url)
        await self.page.wait_for_timeout(400)
        await asyncio.sleep(0.5)

        detail_page_li = await self.list_page_parser()

        if not detail_page_li:
            self.logger.warning(
                'No data found for 市场监督管理总局 %s for dates %s--%s', self.url, self.start_date,
                self.end_date
            )

        for pg in detail_page_li:
            await self.details_pg_processor(pg_data=pg)

    async def list_page_parser(self):
        """
        parse news list
        :return:
        """
        res = []

        html_text = await self.page.content()
        html: _Element = etree.HTML(html_text, etree.HTMLParser(encoding="utf-8"))

        ul_list: List[_Element] = html.xpath(
            '//div[@class="Three_zhnlist_02"]//ul'
        )
        res.extend(self.per_line_parser(ul_list))

        last_pg_date_str = ''.join(
            ul_list[-1].xpath('./li/text()')
        ).strip()
        last_pg_date = datetime.strptime(last_pg_date_str, self.timestamp_format).date()

        while last_pg_date >= datetime.strptime(self.start_date, self.timestamp_format).date():
            self.logger.info('Next pages')
            await self.page.locator('//a[@class="layui-laypage-next text-tag"]').click()
            await self.page.wait_for_timeout(350)
            await asyncio.sleep(0.3)
            next_pg_text = await self.page.content()

            next_html: _Element = etree.HTML(
                next_pg_text,
                etree.HTMLParser(encoding="utf-8", remove_comments=False)
            )
            nex_lr_list: List[_Element] = next_html.xpath(
                '//div[@class="Three_zhnlist_02"]//ul'
            )
            res.extend(self.per_line_parser(nex_lr_list))

            _last_pg_date_str = ''.join(
                nex_lr_list[-1].xpath('./li/text()')
            ).strip()
            if not _last_pg_date_str:
                _last_pg_date_str = ''.join(
                    nex_lr_list[-2].xpath('./li/text()')
                ).strip()
            last_pg_date = datetime.strptime(_last_pg_date_str, self.timestamp_format).date()

        self.logger.info('There are %s proclamation items', len(res))
        return res

    async def details_pg_processor(self, pg_data: dict):
        """
        Detail page processor

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
            self.logger.info('Detail pageStart collecting %s', _link)

            pg_content = self.details_pg_parser(html_text=html_text, pg_data=pg_data)

            _title = re.sub(r'\s+', '', pg_data["title"])
            detail_page_html_file = (
                    self.output_dir /
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
                    self.output_dir /
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
        texts = html.xpath('//div[@class="Three_xilan_02"]//text()')
        cleaned_texts = [clean_text(text) for text in texts]

        all_related_links = []
        for _a in html.xpath('//div[@class="Three_xilan_02"]//a'):
            if ''.join(_a.xpath('./@href')).strip() == '#':
                continue
            all_related_links.append(
                f'''
{''.join(_a.xpath('.//text()'))} {'/'.join(self.page.url.split('/')[:3])}{''.join(_a.xpath('./@href'))}
                '''.strip()
            )

        all_appendix = []
        for _a in html.xpath(xpath_query):
            all_appendix.append(
                f'''
{''.join(_a.xpath('.//text()'))} {'/'.join(self.page.url.split('/')[:3])}{''.join(_a.xpath('./@href'))}
                '''.strip()
            )

        editor_tg = html.xpath('//div[@class="Three_xilan01_01"]//ul[@class="dw"]')[1]
        editor = clean_text(
            ''.join(
                editor_tg.xpath('./li[@class="Three_xilan01_02 Three_xilan01_0201 text-tag"]/text()')
            ))

        return {
            'text': '\n'.join(cleaned_texts).strip(),
            'appendix': ',\n'.join(all_appendix).replace('\xa0', ''),
            'related_documents': ',\n'.join(all_related_links),
            'title': title,
            'editor': editor,
            'date': ''.join(html.xpath('//meta[@name="PubDate"]/@content'))
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
            _page_date = ''.join(line.xpath('./li[@class="nav04Left02_contenttime text-tag"]//text()')).strip()
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
                _title = ''.join(line.xpath('.//a//text()')).strip()
                _link = f'''{'/'.join(self.page.url.split('/')[:-3])}{''.join(line.xpath('.//a/@href')).strip()}'''
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
        await self.get_public_info()
        await self.stop_page()
        self.logger.info('Data collection completed')

    def build_file_xpath(self):
        """
        Generate an XPath query string based on a list of file types
        :return:
        """
        return " or ".join(
            [f"contains(@href, '{ft}')" for ft in self.file_types]
        )
