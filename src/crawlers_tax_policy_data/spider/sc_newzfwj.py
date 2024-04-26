import asyncio
import re
from datetime import datetime
from pathlib import Path
from typing import List

from lxml import etree

from crawlers_tax_policy_data.config import settings
from crawlers_tax_policy_data.spider.base import BaseSpider
from crawlers_tax_policy_data.storage.local import save_data
from crawlers_tax_policy_data.utils.utils import clean_text, extract_url_base


class ScNewzfwj(BaseSpider):
    """
    四川省人民政府 省政府政策文件 spider
    """
    folder = 'sc.gov.cn/省政府政策文件'

    def __init__(self):
        super().__init__()
        self.start_date, self.end_date = self.check_date
        self.output_dir = Path(
            settings.GOV_OUTPUT_PAHT
        ) / self.folder / f'{self.start_date}-{self.end_date}'

    @property
    def headers(self):
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": "yfx_c_g_u_id_10000001=_ck24042515112816087943581676676; Hm_lvt_da7caec4897c6edeca8fe272db36cca4=1714029089; yfx_f_l_v_t_10000001=f_t_1714029088600__r_t_1714111337714__v_t_1714126931371__r_c_1; _yfxkpy_ssid_10003074=%7B%22_yfxkpy_firsttime%22%3A%221714029088633%22%2C%22_yfxkpy_lasttime%22%3A%221714111337746%22%2C%22_yfxkpy_visittime%22%3A%221714126931392%22%2C%22_yfxkpy_domidgroup%22%3A%221714126931392%22%2C%22_yfxkpy_domallsize%22%3A%22100%22%2C%22_yfxkpy_cookie%22%3A%2220240425151128636721454305856448%22%2C%22_yfxkpy_returncount%22%3A%221%22%7D; Hm_lpvt_da7caec4897c6edeca8fe272db36cca4=1714127066",
            "Host": "www.sc.gov.cn",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Chromium\";v=\"124\", \"Google Chrome\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
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

    async def collector(self, url: str, spider_name: str):
        """
        collector
        :param spider_name:
        :param url:
        :return:
        """

        await self.init_page()
        await self.page.goto(url)
        await self.page.wait_for_timeout(300)
        html_text = await self.page.content()
        self.logger.info('Parse 四川省人民政府 %s data %s', spider_name, url)

        detail_page_li = await self.list_page_parser(html_text, url)

        if not detail_page_li:
            self.logger.warning(
                f'No data found for 四川省人民政府 %s at %s for dates %s-%s', spider_name, url, self.start_date,
                self.end_date
            )

        for pg in detail_page_li:
            await self.details_pg_processor(pg_data=pg)

    async def list_page_parser(
            self,
            html_text: str,
            url: str
    ) -> list:
        """
        list pages parser
        :param url:
        :param html_text:
        :return:
        """
        res = []
        html: etree._Element = etree.HTML(html_text, etree.HTMLParser(encoding="utf-8", remove_comments=False))

        li_list: List[etree._Element] = html.xpath('//div[@class="biaobody"]//li')

        fir_pg_data = self.per_line_parser(li_list)
        res.extend(fir_pg_data)

        last_pg_date_str = ''.join(li_list[-1].xpath('.//div[@class="lie5"]//text()')).strip()
        last_pg_date = datetime.strptime(last_pg_date_str, '%Y-%m-%d').date()

        pg_num = 2
        while last_pg_date >= datetime.strptime(self.start_date, '%Y-%m-%d').date():
            await self.page.goto(f'{url}{pg_num}')
            await self.page.wait_for_timeout(350)

            next_pg_text = await self.page.content()
            next_html: etree._Element = etree.HTML(
                next_pg_text,
                etree.HTMLParser(encoding="utf-8", remove_comments=False)
            )
            nex_li_list: List[etree._Element] = next_html.xpath('//div[@class="biaobody"]//li')
            res.extend(self.per_line_parser(nex_li_list))

            _last_pg_date_str = ''.join(nex_li_list[-1].xpath('.//div[@class="lie5"]//text()')).strip()
            last_pg_date = datetime.strptime(_last_pg_date_str, '%Y-%m-%d').date()
            pg_num += 1
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

    def details_pg_parser(self, html_text: str):
        """
        Details page parser
        :param html_text:
        :return:
        """
        current_pg_url = self.page.url
        file_xpath = self.build_file_xpath()
        xpath_query = f'//a[{file_xpath}]'

        html: etree._Element = etree.HTML(
            html_text,
            etree.HTMLParser(encoding="utf-8")  # fix garbled characters in requests
        )
        texts = html.xpath('//div[@class="contText"]//text()')
        cleaned_texts = [clean_text(text) for text in texts]

        all_related_links = extract_related_links(html, '//div[@id="xqygb22"]//li//a', 'https://www.sc.gov.cn')
        all_related_links = list(set(all_related_links))
        all_appendix = extract_related_links(html, xpath_query, f'{extract_url_base(current_pg_url)}/')
        all_appendix = list(set(all_appendix))
        return {
            'text': '\n'.join(cleaned_texts).strip(),
            'related_documents': ',\n'.join(all_related_links),
            'appendix': ',\n'.join(all_appendix).replace('\xa0', ''),
            'state': ''.join(html.xpath('//span[@id="invalidTime"]/text()')).strip()
        }

    async def details_pg_processor(self, pg_data: dict):
        """
        Details page processor
        :param pg_data:
        :return:
        """
        _link = pg_data.get('link')

        if 'pdf' in _link:
            content = {key: pg_data[key] for key in ['link', 'date', 'title', 'editor']}

        else:
            await self.page.goto(_link)
            await self.page.wait_for_timeout(350)
            html_text = await self.page.content()
            content = self.details_pg_parser(html_text=html_text)

            _title = re.sub(r'\s+', '', pg_data["title"])
            detail_page_html_file = self.output_dir / f'''{pg_data['date']}-{_title}.html'''
            self.save_html(
                html_content=html_text,
                file=detail_page_html_file
            )

            content.update({key: pg_data[key] for key in ['link', 'date', 'title', 'editor']})
            content.update({'html_file': str(detail_page_html_file)})

        save_data(
            content=content,
            file_path=self.output_dir / f"{self.start_date}-{self.end_date}-public"
                                        f"-information.csv"
        )
        await asyncio.sleep(0.3)


def extract_related_links(html, xpath, prefix: str):
    """
    Extract the links according to the given XPath
    :param prefix:
    :param html:
    :param xpath:
    :return:
    """
    return [f'{"".join(link.xpath("./text()"))} {prefix}{"".join(link.xpath("@href"))}'.strip() for link in
            html.xpath(xpath)]
