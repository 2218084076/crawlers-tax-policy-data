"""
工业和信息化部
https://www.miit.gov.cn/search/wjfb.html?websiteid=110000000000000&pg=&p=&tpl=14&category=51&q=
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


class MiitSpider(BaseSpider):
    """
    工业和信息化部 spider
    """
    folder = 'miit.gov.cn'

    def __init__(self):
        super().__init__()
        self.start_date, self.end_date = self.check_date
        self.output_dir = Path(
            settings.GOV_OUTPUT_PAHT
        ) / self.folder / f'{self.start_date}-{self.end_date}'
        self.timestamp_format = '%Y-%m-%d'
        self.url_prefix = 'https://www.miit.gov.cn'

    @property
    def url(self):
        """
        url
        :return:
        """
        return 'https://www.miit.gov.cn/search/wjfb.html?websiteid=110000000000000&pg=&p=&tpl=14&category=51&q='

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
            'Start collecting 工业和信息化部 %s %s-%s data',
            self.url, self.start_date, self.end_date
        )
        await self.init_page()
        await self.page.goto(self.url)
        await self.page.wait_for_timeout(350)
        await asyncio.sleep(0.5)

        detail_page_li = await self.list_page_parser()

        if not detail_page_li:
            self.logger.warning(
                'No data found for 国家外汇管理局 %s for dates %s-%s', self.url, self.start_date, self.end_date
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
        html: etree._Element = etree.HTML(html_text, etree.HTMLParser(encoding="utf-8"))

        lr_list: List[etree._Element] = html.xpath(
            '//div[@class="yyfw_box"]//div[@class="jcse-result-box search-list"]'
        )
        res.extend(self.per_line_parser(lr_list))

        last_pg_date_str = extract_pg_date(html=lr_list[-1])
        last_pg_date = datetime.strptime(last_pg_date_str, '%Y-%m-%d').date()

        while last_pg_date >= datetime.strptime(self.start_date, '%Y-%m-%d').date():
            await self.page.locator('//div[@id="pagination"]//a[last()]').click()
            await self.page.wait_for_timeout(350)
            await asyncio.sleep(0.3)
            next_pg_text = await self.page.content()

            next_html: etree._Element = etree.HTML(
                next_pg_text,
                etree.HTMLParser(encoding="utf-8", remove_comments=False)
            )
            nex_lr_list: List[etree._Element] = next_html.xpath(
                '//div[@class="yyfw_box"]//div[@class="jcse-result-box search-list"]'
            )
            res.extend(self.per_line_parser(nex_lr_list))

            _last_pg_date_str = extract_pg_date(nex_lr_list[-1])
            last_pg_date = datetime.strptime(_last_pg_date_str, '%Y-%m-%d').date()
        self.logger.info('There are %s proclamation items', len(res))
        return res

    async def details_pg_processor(self, pg_data: dict):
        """
        Detail page processor

        Parse each detail page to extract news data
        The `pg_data` format is
        {
            'title': _title,
            'link': _link,
            'date': _page_date,
        }
        :param pg_data:
        :return:
        """
        _link = pg_data['link']

        if '.pdf' in _link:
            pg_content = {key: pg_data[key] for key in ['link', 'date', 'title']}

        else:
            await self.page.goto(_link)
            await self.page.wait_for_timeout(350)
            html_text = await self.page.content()

            pg_content = self.details_pg_parser(html_text=html_text, pg_data=pg_data)

            _title = re.sub(r'\s+', '', pg_data["title"])
            detail_page_html_file = self.output_dir / f'''{pg_data['date']}-{_title}.html'''
            self.save_html(
                html_content=html_text,
                file=detail_page_html_file
            )

            pg_content.update({key: pg_data[key] for key in ['link', 'date']})
            pg_content.update({'html_file': str(detail_page_html_file)})

        save_data(
            content=pg_content,
            file_path=self.output_dir / f"{self.start_date}-{self.end_date}-public"
                                        f"-information.csv"
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
        self.logger.info('details page parser %s', pg_data['link'])

        _url_prefix = '/'.join(pg_data['link'].split('/')[:-1])

        file_xpath = self.build_file_xpath()
        xpath_query = f'//a[{file_xpath}]'

        html = etree.HTML(
            html_text,
            etree.HTMLParser(encoding="utf-8")  # fix garbled characters in requests
        )
        title = ''.join(html.xpath('//h1[@id="con_title"]/text()')).strip()
        # Analyze document number & top information
        top_info_list = []
        editor = ''
        for p in html.xpath('//div[@class="xxgk-box"]//p'):
            p_content = p.xpath('./span/text()')
            if '发文字号' in p_content:
                editor = p_content[-1].strip()
            top_info_list.append(''.join(p_content))
        top_info = '\n'.join(top_info_list)
        c_title = ''.join(html.xpath('//h1[@id="con_title"]//text()')).strip()

        texts = '\n'.join(html.xpath('//div[@id="con_con"]//p//text()'))

        all_related_links = extract_related_links(html, '//div[@class="detail-news"]//p/a', '')

        all_appendix = extract_related_links(html, xpath_query, _url_prefix)
        _res = {
            'title': title,
            'text': f'''{top_info}\n\n{c_title}\n\n{texts}''',
            'appendix': ',\n'.join(all_appendix).replace('\xa0', ''),
            'related_documents': ',\n'.join(list(set(all_related_links))),
            'editor': editor
        }
        return _res

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
            _page_date = extract_pg_date(html=line)
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
                _title = ''.join(line.xpath('./div[@class="search-list-t"]/a/text()')).strip()
                _link = f'''{self.url_prefix}{''.join(line.xpath('./div[@class="search-list-t"]/a/@href')).strip()}'''
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


def extract_related_links(html, xpath, prefix: str):
    """
    Extract the links according to the given XPath
    :param prefix:
    :param html:
    :param xpath:
    :return:
    """
    return [
        f'{"".join(list(set(link.xpath(".//text()")))).strip()} {prefix}/{"".join(link.xpath("@href"))}'.strip() for
        link in
        html.xpath(xpath)
    ]


def extract_pg_date(html):
    """
    extract_pages_date
    :param html:
    :return:
    """
    _pg_span_list = html.xpath('.//div[@class="search-list-b"]//span')
    date_regex = re.compile(r'\d{4}-\d{2}-\d{2}')
    _page_date = next((span.text for span in _pg_span_list if date_regex.match(span.text)), None)
    return _page_date
