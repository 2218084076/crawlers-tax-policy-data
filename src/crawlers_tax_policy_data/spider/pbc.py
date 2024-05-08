"""
中国人民银行
http://www.pbc.gov.cn/tiaofasi/144941/3581332/index.html
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


class PbcSpider(BaseSpider):
    """
    中国人民银行 spider
    """
    folder = 'pbc.gov.cn'

    def __init__(self):
        super().__init__()
        self.start_date, self.end_date = self.check_date
        self.output_dir = Path(
            settings.GOV_OUTPUT_PAHT
        ) / self.folder / f'{self.start_date}-{self.end_date}'
        self.timestamp_format = '%Y-%m-%d'
        self.url_prefix = 'http://www.pbc.gov.cn'

    @property
    def url(self):
        """
        url
        :return:
        """
        return 'http://www.pbc.gov.cn/tiaofasi/144941/3581332/3b3662a6/index'

    @property
    def headers(self):
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
                      "application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": "wzws_sessionid=gDE4MC4xNjkuMTI4LjM5gjc0Y2Y0MaBmOzIQgWExNmRkYQ==; wzws_cid=f497945f305d1dc7bdd35"
                      "234e263fdbc52278d685b8734c9ae91728c4417172b5d4d480dd9112c2c171fd655eca565aecac993405820c16e037f"
                      "f87f4e9ea3b657af322907ce0326a479056b774c1045",
            "Host": "www.pbc.gov.cn",
            "If-Modified-Since": "Fri, 15 Mar 2024 09:01:55 GMT",
            "If-None-Match": "W/\"20c902-9931-613af426e66c0\"",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124."
                          "0.0.0 Safari/537.36"
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
        _url = f'{self.url}1.html'
        self.logger.info(
            'Start collecting 中国人民银行 %s %s-%s data',
            _url, self.start_date, self.end_date
        )
        await self.init_page()
        await self.page.goto(_url)
        await self.page.wait_for_timeout(350)
        await asyncio.sleep(0.5)

        detail_page_li = await self.list_page_parser()

        if not detail_page_li:
            self.logger.warning(
                'No data found for 国家外汇管理局 %s for dates %s--%s', self.url, self.start_date, self.end_date
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

        lr_list: List[etree._Element] = [
            i for i in html.xpath('//div[@class="portlet"]//table') if
            '首页' not in i.xpath('.//text()')
        ]
        res.extend(self.per_line_parser(lr_list))

        last_pg_date_str = ''.join(lr_list[-1].xpath('.//span[@class="hui12"]/text()')).strip()
        last_pg_date = datetime.strptime(last_pg_date_str, '%Y-%m-%d').date()

        _p_num = 2
        while last_pg_date >= datetime.strptime(self.start_date, '%Y-%m-%d').date():
            _next_url = f'{self.url}{_p_num}.html'
            self.logger.info('Next pages %s', _next_url)
            await self.page.goto(_next_url)
            await self.page.wait_for_timeout(350)
            await asyncio.sleep(0.3)
            next_pg_text = await self.page.content()

            next_html: etree._Element = etree.HTML(
                next_pg_text,
                etree.HTMLParser(encoding="utf-8", remove_comments=False)
            )
            nex_lr_list: List[etree._Element] = [
                i for i in next_html.xpath('//div[@class="portlet"]//table') if
                '首页' not in i.xpath('.//text()')
            ]
            res.extend(self.per_line_parser(nex_lr_list))

            _last_pg_date_str = ''.join(
                nex_lr_list[-1].xpath('.//span[@class="hui12"]/text()')
            ).strip()
            last_pg_date = datetime.strptime(_last_pg_date_str, '%Y-%m-%d').date()
            _p_num += 1

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
            self.logger.info('Detail pageStart collecting %s', _link)
            await self.page.wait_for_timeout(350)
            html_text = await self.page.content()

            pg_content = self.details_pg_parser(html_text=html_text, pg_data=pg_data)

            _title = re.sub(r'\s+', '', pg_data["title"])
            match = re.search(pattern, pg_content['title'])
            try:
                editor = match.group()
            except AttributeError:
                editor = ''
            detail_page_html_file = self.output_dir / f'''{pg_data['date']}-{_title}.html'''
            self.save_html(
                html_content=html_text,
                file=detail_page_html_file
            )

            pg_content.update({key: pg_data[key] for key in ['link', 'date']})
            pg_content.update({'editor': editor})
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
        deatil page parser
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

        texts = html.xpath('//td[@class="content"]//text()')
        cleaned_texts = [clean_text(text) for text in texts]

        all_related_links = extract_related_links(html, '//td[@class="content"]//p/a', self.url_prefix)

        all_appendix = extract_related_links(html, xpath_query, self.url_prefix)
        return {
            'text': '\n'.join(cleaned_texts).strip(),
            'appendix': ',\n'.join(all_appendix).replace('\xa0', ''),
            'related_documents': ',\n'.join(list(set(all_related_links))),
            'title': ''.join(html.xpath('//td[@align="center"]/h2/text()')).strip()
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
            _page_date = ''.join(line.xpath('.//span[@class="hui12"]/text()')).strip()
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
                _title = ''.join(line.xpath('.//font[@class="newslist_style"]/a/text()')).strip()
                _link = f'''{self.url_prefix}{''.join(line.xpath('.//font[@class="newslist_style"]/a/@href')).strip()}'''
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
        f'{"".join(list(set(link.xpath(".//text()")))).strip()} {prefix}{"".join(link.xpath("@href"))}'.strip() for
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
