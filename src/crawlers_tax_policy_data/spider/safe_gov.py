"""
国家外汇管理局
https://www.safe.gov.cn/safe/zcfg/index.html
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
        self.timestamp_format = '%Y-%m-%d'
        self.url_prefix = 'https://www.safe.gov.cn'

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
        self.logger.info('get %s', self.page)

        detail_page_li = await self.list_page_parser()

        if not detail_page_li:
            self.logger.warning(
                f'No data found for 国家外汇管理局 %s for dates %s-%s', self.url, self.start_date, self.end_date
            )

        for pg in detail_page_li:
            await self.details_pg_processor(pg_data=pg)

    async def list_page_parser(self):
        """
        parse news list
        :param html_text:
        :return:
        """
        res = []
        html_text = await self.page.content()
        html = etree.HTML(html_text, etree.HTMLParser(encoding="utf-8"))

        li_list: List[etree._Element] = html.xpath('//div[@class="list_conr"]//li')
        res.extend(self.per_line_parser(li_list))

        last_pg_date_str = ''.join(li_list[-1].xpath('./dd/text()')).strip()
        last_pg_date = datetime.strptime(last_pg_date_str, '%Y-%m-%d').date()

        while last_pg_date >= datetime.strptime(self.start_date, '%Y-%m-%d').date():
            await self.page.locator('//a[@title="下一页"]').click()
            await self.page.wait_for_timeout(350)
            next_pg_text = await self.page.content()

            next_html: etree._Element = etree.HTML(
                next_pg_text,
                etree.HTMLParser(encoding="utf-8", remove_comments=False)
            )
            nex_li_list: List[etree._Element] = next_html.xpath('//div[@class="list_conr"]//li')
            res.extend(self.per_line_parser(nex_li_list))

            _last_pg_date_str = ''.join(nex_li_list[-1].xpath('./dd/text()')).strip()
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

            pg_content = self.details_pg_parser(html_text=html_text)

            _title = re.sub(r'\s+', '', pg_data["title"])
            detail_page_html_file = self.output_dir / f'''{pg_data['date']}-{_title}.html'''
            self.save_html(
                html_content=html_text,
                file=detail_page_html_file
            )

            pg_content.update({key: pg_data[key] for key in ['link', 'date', 'title']})
            pg_content.update({'html_file': str(detail_page_html_file)})

        save_data(
            content=pg_content,
            file_path=self.output_dir / f"{self.start_date}-{self.end_date}-public"
                                        f"-information.csv"
        )
        await asyncio.sleep(0.5)

    def details_pg_parser(
            self,
            html_text: str
    ):
        """
        deatil page parser
        :param html_text:
        :return:
        """
        _url_prefix = 'https://www.safe.gov.cn'

        file_xpath = self.build_file_xpath()
        xpath_query = f'//a[{file_xpath}]'

        html: etree._Element = etree.HTML(
            html_text,
            etree.HTMLParser(encoding="utf-8")  # fix garbled characters in requests
        )
        title = ''.join(html.xpath('//div[@class="detail_tit"]//text()')).strip()

        editor = ''.join(html.xpath('//span[@id="wh"]//text()')).strip()

        all_related_links = extract_related_links(html, '//div[@class="list_conr"]//a', _url_prefix)

        all_appendix = extract_related_links(html, xpath_query, _url_prefix)

        # 正文
        condition = html.xpath('//div[@class="detail_conbg"]//div[@class="condition"]//text()')
        detail_tit = html.xpath('//div[@class="detail_conbg"]//div[@class="detail_tit"]//text()')
        detail_content = html.xpath('//div[@class="detail_conbg"]//div[@class="detail_content"]//text()')
        condition_txt = []
        is_previous_empty = False
        empty_count = 0
        for con in condition:
            if con.strip() == '':
                empty_count += 1
                if empty_count == 2:
                    condition_txt.pop()  # Remove the previous space added for single empty string
                    condition_txt.append('\n')
                    empty_count = 0
                else:
                    if not is_previous_empty:
                        condition_txt.append(' ')
                is_previous_empty = True
            else:
                condition_txt.append(con.strip())
                is_previous_empty = False
                empty_count = 0

        return {
            'title': title,
            'text': f'''{''.join(condition_txt).strip()}\n\n{''.join(detail_tit)}\n\n{''.join(detail_content)}''',
            'editor': editor,
            'appendix': ',\n'.join(all_appendix).replace('\xa0', ''),
            'related_documents': ',\n'.join(list(set(all_related_links))),
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
        prefix = 'https://www.safe.gov.cn'
        for line in li_list_html:
            _page_date = ''.join(line.xpath('./dd/text()')).strip()
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
                _link = f'''{prefix}{''.join(line.xpath('.//a/@href')).strip()}'''

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


def extract_related_links(html, xpath, prefix: str):
    """
    Extract the links according to the given XPath
    :param prefix:
    :param html:
    :param xpath:
    :return:
    """
    return [f'{"".join(list(set(link.xpath(".//text()"))))} {prefix}{"".join(link.xpath("@href"))}'.strip() for link in
            html.xpath(xpath)]
