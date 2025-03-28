"""
证监会
http://www.csrc.gov.cn/csrc/c101954/zfxxgk_zdgk.shtml
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


class CsrcSpider(BaseSpider):
    """
    证监会 spider
    """
    folder = 'csrc.gov.cn'

    def __init__(self):
        super().__init__()
        self.start_date, self.end_date = self.check_date
        self.output_dir = Path(
            settings.GOV_OUTPUT_PAHT
        ) / self.folder / f'{self.start_date}-{self.end_date}'
        self.timestamp_format = '%Y-%m-%d'
        self.url_prefix = 'https://www.safe.gov.cn'

    @property
    def url(self):
        """
        url
        :return:
        """
        return 'http://www.csrc.gov.cn/csrc/c101954/zfxxgk_zdgk.shtml'

    @property
    def headers(self):
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
                      "application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": "acw_tc=3adc342617150047531305823e2eda2e180285a83b145408ec7a6fde6b; _gscu_516223281=15004753iobsst"
                      "13; _gscbrs_516223281=1; _gscs_516223281=15004753prmp7313|pv:1; _yfxkpy_ssid_10008998=%7B%22_yfxk"
                      "py_firsttime%22%3A%221715004753890%22%2C%22_yfxkpy_lasttime%22%3A%221715004753890%22%2C%22_yfxkpy"
                      "_visittime%22%3A%221715004753890%22%2C%22_yfxkpy_domidgroup%22%3A%221715004753890%22%2C%22_yfxkpy"
                      "_domallsize%22%3A%22100%22%2C%22_yfxkpy_cookie%22%3A%2220240506221233896699419945353686%22%7D",
            "Host": "www.csrc.gov.cn",
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
        self.logger.info(
            'Start collecting 证监会 %s %s-%s data',
            self.url, self.start_date, self.end_date
        )
        await self.init_page()
        await self.page.goto(self.url)
        await self.page.wait_for_timeout(350)

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
        html = etree.HTML(html_text, etree.HTMLParser(encoding="utf-8"))

        lr_list: List[etree._Element] = html.xpath('//ul[@class="list_ul"]/table/tbody//tr')[1:]
        res.extend(self.per_line_parser(lr_list))

        last_pg_date_str = ''.join(lr_list[-1].xpath('.//span[@class="date"]/text()')).strip()
        last_pg_date = datetime.strptime(last_pg_date_str, '%Y-%m-%d').date()

        while last_pg_date >= datetime.strptime(self.start_date, '%Y-%m-%d').date():
            await self.page.locator('//a[@class="nextbtn"]').click()
            await self.page.wait_for_timeout(350)
            next_pg_text = await self.page.content()

            next_html: etree._Element = etree.HTML(
                next_pg_text,
                etree.HTMLParser(encoding="utf-8", remove_comments=False)
            )
            nex_lr_list: List[etree._Element] = next_html.xpath('//ul[@class="list_ul"]/table/tbody//tr')[1:]
            res.extend(self.per_line_parser(nex_lr_list))

            _last_pg_date_str = ''.join(nex_lr_list[-1].xpath('.//span[@class="date"]/text()')).strip()
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
            repo = await self.async_get_req(
                url=_link,
                headers=self.headers
            )
            repo.encoding = 'utf-8'
            html_text = repo.text

            pg_content = self.details_pg_parser(html_text=html_text, pg_data=pg_data)

            _title = re.sub(r'\s+', '', pg_data["title"])
            detail_page_html_file = self.output_dir / f'''{pg_data['date']}-{_title}.html'''
            self.save_html(
                html_content=html_text,
                file=detail_page_html_file
            )

            pg_content.update({key: pg_data[key] for key in ['link', 'date', 'editor']})
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
        _url_prefix = '/'.join(pg_data['link'].split('/')[:-1])

        file_xpath = self.build_file_xpath()
        xpath_query = f'//a[{file_xpath}]'

        html: etree._Element = etree.HTML(
            html_text,
            etree.HTMLParser(encoding="utf-8")  # fix garbled characters in requests
        )
        title = ''.join(html.xpath('//meta[@name="ArticleTitle"]/@content')).strip()

        # Content Parsing Modul
        xxgk_table = [tab.strip() for tab in html.xpath('//div[@class="content"]//div[@class="xxgk-table"]//text()')]
        detail_tit = html.xpath('//div[@class="content"]/h2//text()')
        text = html.xpath('//div[@class="content"]/div[@class="detail-news"]//text()')
        info_list = []
        empty_text = 0
        for t in xxgk_table:
            if t == '':
                empty_text += 1
            else:
                if empty_text <= 2:
                    info_list.append(' ')
                elif empty_text > 2:
                    info_list.append('\n')
                info_list.append(t)
                empty_text = 0

        all_related_links = extract_related_links(html, '//div[@class="detail-news"]//p/a', '')

        all_appendix = extract_related_links(html, xpath_query, _url_prefix)
        res = {
            'title': title,
            'text': f'''{''.join(info_list)}\n\n{''.join(detail_tit)}\n\n{''.join(text)}''',
            'appendix': ',\n'.join(all_appendix).replace('\xa0', ''),
            'related_documents': ',\n'.join(list(set(all_related_links))),
        }
        return res

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
            _page_date = ''.join(line.xpath('.//span[@class="date"]/text()')).strip()
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
                _title = ''.join(line.xpath('./td[@class="info bt"]/a/text()')).strip()
                _link = ''.join(line.xpath('./td[@class="info bt"]/a/@href')).strip()
                _editor = ''.join(line.xpath('./td[@class="fwrq"]/text()'))
                res.append({
                    'title': _title,
                    'link': _link,
                    'date': _page_date,
                    'editor': _editor
                })
        return res

    async def run(self):
        """
        run crawlers
        :return:
        """
        self.logger.info('start running crawlers...')
        await self.get_public_info()


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
