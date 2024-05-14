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

    async def get_public_info(self, spider_name: str):
        """
        get public info
        :param spider_name:
        :return:
        """
        crawlers = crawlers_categories[spider_name]

        self.logger.info(
            'Start collecting 银保监会 %s %s %s--%s data',
            crawlers['name'], self.url, self.start_date, self.end_date
        )

        await self.init_page()
        await self.page.goto(self.url)
        await self.page.wait_for_timeout(400)
        span_id = await self.page.locator('//span[@class="item-class ng-binding active"]').get_attribute('item')
        if span_id != crawlers['item_id']:
            await self.page.locator(crawlers['tag_xpath']).click()
        await self.page.wait_for_timeout(350)
        await asyncio.sleep(0.5)

        detail_page_li = await self.list_page_parser(crawlers)

        if not detail_page_li:
            self.logger.warning(
                'No data found for 国家发改委 %s %s for dates %s--%s', crawlers['name'], self.url, self.start_date,
                self.end_date
            )

        for pg in detail_page_li:
            await self.details_pg_processor(pg_data=pg, spider_name=spider_name)

    async def list_page_parser(self, crawlers: dict):
        """
        parse news list
        :return:
        """
        res = []

        span_id = await self.page.locator('//span[@class="item-class ng-binding active"]').get_attribute('item')
        if span_id != crawlers['item_id']:
            await self.page.locator(crawlers['tag_xpath']).click()
        await self.page.wait_for_timeout(350)

        html_text = await self.page.content()
        html: etree._Element = etree.HTML(html_text, etree.HTMLParser(encoding="utf-8"))

        li_list: List[etree._Element] = html.xpath(
            '//div[@class="zhengfuxinxi-list guizhang zhengce-fgz"]/div[@class="zhengfuxinxi-list-ul"]//li'
        )
        res.extend(self.per_line_parser(li_list))

        last_pg_date_str = ''.join(
            li_list[-1].xpath('./span[@class="zhengfuxinxi-list-date ng-binding"]/text()')
        ).strip()
        last_pg_date = datetime.strptime(last_pg_date_str, self.timestamp_format).date()

        while last_pg_date >= datetime.strptime(self.start_date, self.timestamp_format).date():
            self.logger.info('Next pages')
            await self.page.locator('//div[@ng-show="zcFlag"][last()]//a[@ng-click="pager.next()"]').click()
            await self.page.wait_for_timeout(350)
            await asyncio.sleep(0.3)
            next_pg_text = await self.page.content()

            next_html: etree._Element = etree.HTML(
                next_pg_text,
                etree.HTMLParser(encoding="utf-8", remove_comments=False)
            )
            nex_lr_list: List[etree._Element] = next_html.xpath(
                '//div[@class="zhengfuxinxi-list guizhang zhengce-fgz"]/div[@class="zhengfuxinxi-list-ul"]//li'
            )
            res.extend(self.per_line_parser(nex_lr_list))

            _last_pg_date_str = ''.join(
                nex_lr_list[-1].xpath('./span[@class="zhengfuxinxi-list-date ng-binding"]/text()')
            ).strip()
            last_pg_date = datetime.strptime(_last_pg_date_str, self.timestamp_format).date()

        self.logger.info('There are %s proclamation items', len(res))
        return res

    async def details_pg_processor(self, pg_data: dict, spider_name: str):
        """
        Detail page processor

        :param pg_data:
        :param spider_name:
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
                    crawlers_categories[spider_name]['name'] /
                    f'''{pg_data['date']}{_title}.html'''.replace('/', '')
            )
            self.save_html(
                html_content=html_text,
                file=detail_page_html_file
            )

            pg_content.update({key: pg_data[key] for key in ['link', 'date']})
            pg_content.update({'html_file': str(detail_page_html_file)})

        save_data(
            content=pg_content,
            file_path=(
                    self.output_dir /
                    crawlers_categories[spider_name]['name'] /
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
        texts = html.xpath('//div[@class="content newcontent"]//div[@class="row"]//text()')
        cleaned_texts = [clean_text(text) for text in texts]

        all_related_links = []

        all_appendix = []
        for i in html.xpath('//div[@class="content newcontent"]//div[@class="row"]//p'):

            _u = ''.join(i.xpath('.//a/@href')).strip()
            if _u:
                _t = ''.join(i.getprevious().xpath('.//span//text()')).strip()
                _item = f'''{_t} {_u}'''
                all_appendix.append(_item)

        return {
            'text': '\n'.join(cleaned_texts).strip(),
            'appendix': ',\n'.join(all_appendix).replace('\xa0', ''),
            'related_documents': '\n'.join(all_related_links),
            'title': title,
            'editor': ''.join(html.xpath('//div[@class="ItemDetailRed-header-row34"]/span/span/text()')).strip()
        }

    def per_line_parser(
            self,
            li_list_html: List[etree._Element]
    ) -> List[Dict[str, str]]:
        """
        Per-line parser

        使用 `-` 格式日期
        :param li_list_html:
        :return:
        """
        res = []
        for line in li_list_html:
            _page_date = ''.join(line.xpath('./span[@class="zhengfuxinxi-list-date ng-binding"]/text()')).strip()
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
                _link = f'''{'/'.join(self.page.url.split('/')[:-5])}{''.join(line.xpath('.//a/@href')).strip()}'''
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
        spider_tasks = settings.CBIRC_SPIDER
        for _s in spider_tasks:
            await self.get_public_info(spider_name=_s)
            await self.stop_page()
