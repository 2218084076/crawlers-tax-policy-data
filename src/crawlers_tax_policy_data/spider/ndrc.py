"""
国家发改委
https://www.ndrc.gov.cn/xxgk/zcfb/fzggwl/ 发展改革委令 fzggwl
https://www.ndrc.gov.cn/xxgk/zcfb/ghxwj/ 规范性文件 ghxwj
https://www.ndrc.gov.cn/xxgk/zcfb/gg/    公告 gg
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
    'fzggwl': {'name': '发展改革委令', 'suffix': '/fzggwl/index'},
    'ghxwj': {'name': '规范性文件', 'suffix': '/ghxwj/index'},
    'gg': {'name': '公告', 'suffix': '/gg/index'},
}


class NdrcSpider(BaseSpider):
    """
    国家发改委 spider
    """
    folder = 'ndrc.gov.cn'

    def __init__(self):
        super().__init__()
        self.start_date, self.end_date = self.check_date
        self.output_dir = Path(
            settings.GOV_OUTPUT_PAHT
        ) / self.folder / f'{self.start_date}-{self.end_date}'.replace('/', '')
        self.timestamp_format = '%Y/%m/%d'
        self.url_prefix = 'http://www.pbc.gov.cn'

    @property
    def url(self):
        """
        url
        :return:
        """
        return 'https://www.ndrc.gov.cn/xxgk/zcfb'

    @property
    def headers(self):
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
                      "application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": "Hm_lvt_6c8165462fd93121348afe212168341f=1715159396; http_waf_cookie=61b98b5d-59d8-440db48fe415b36"
                      "aea7937379d5ce14bb4a2; SF_cookie_3=21321202; wzaIsOn=true; readScreen=true; speakVolume=0; readSt"
                      "atus=pointRead; batchReadIsOn=false; guidesStatus=off; highContrastMode=defaltMode; cursorStatus="
                      "off; magnifierIsOn=true; _yfxkpy_ssid_10005970=%7B%22_yfxkpy_firsttime%22%3A%221715159400876%22%2"
                      "C%22_yfxkpy_lasttime%22%3A%221715159400876%22%2C%22_yfxkpy_visittime%22%3A%221715166800758%22%2C%"
                      "22_yfxkpy_domidgroup%22%3A%221715166800758%22%2C%22_yfxkpy_domallsize%22%3A%22100%22%2C%22_yfxkpy"
                      "_cookie%22%3A%2220240508171000878644836513624963%22%7D; Hm_lpvt_6c8165462fd93121348afe212168341f="
                      "1715166817",
            "Host": "www.ndrc.gov.cn",
            "Referer": "https://www.ndrc.gov.cn/xxgk/zcfb/fzggwl/index.html",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124."
                          "0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Chromium\";v=\"124\", \"Google Chrome\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0"
        }

    @property
    def check_date(self) -> tuple:
        """
        check date
        :return:
        """
        check_date = self.date
        if isinstance(check_date, dict):
            start_date = f'{check_date["start"].year}/{int(check_date["start"].month):02d}/{int(check_date["start"].day):02d}'
            end_date = f'{check_date["end"].year}/{int(check_date["end"].month):02d}/{int(check_date["end"].day):02d}'
        else:
            start_date = f'{check_date.year}/{int(check_date.month):02d}/{int(check_date.day):02d}'
            end_date = f'{check_date.year}/{int(check_date.month):02d}/{int(check_date.day):02d}'
        return start_date, end_date

    async def get_public_info(self, spider_name: str):
        """
        get public info
        :param spider_name:
        :return:
        """
        crawlers = crawlers_categories[spider_name]
        _url = f'{self.url}{crawlers["suffix"]}.html'

        self.logger.info(
            'Start collecting 国家发改委 %s %s %s-%s data',
            crawlers['name'], _url, self.start_date, self.end_date
        )

        await self.init_page()
        await self.page.goto(_url)
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
        html_text = await self.page.content()
        html: etree._Element = etree.HTML(html_text, etree.HTMLParser(encoding="utf-8"))

        li_list: List[etree._Element] = html.xpath('//ul[@class="u-list"]/li[not(@class="empty")]')
        res.extend(self.per_line_parser(li_list))

        last_pg_date_str = ''.join(li_list[-1].xpath('./span/text()')).strip()
        last_pg_date = datetime.strptime(last_pg_date_str, '%Y/%m/%d').date()

        _p_num = 1
        while last_pg_date >= datetime.strptime(self.start_date, '%Y/%m/%d').date():
            # 下一页 click xpath
            # //div[@class="page"]//li[@class="cur"][last()]/a
            _next_url = f'{self.url}{crawlers["suffix"]}_{_p_num}.html'
            self.logger.info('Next pages %s', _next_url)
            await self.page.goto(_next_url)
            await self.page.wait_for_timeout(350)
            await asyncio.sleep(0.3)
            next_pg_text = await self.page.content()

            next_html: etree._Element = etree.HTML(
                next_pg_text,
                etree.HTMLParser(encoding="utf-8", remove_comments=False)
            )
            nex_lr_list: List[etree._Element] = next_html.xpath('//ul[@class="u-list"]/li[not(@class="empty")]')
            res.extend(self.per_line_parser(nex_lr_list))

            _last_pg_date_str = ''.join(
                nex_lr_list[-1].xpath('./span/text()')
            ).strip()
            last_pg_date = datetime.strptime(_last_pg_date_str, '%Y/%m/%d').date()
            _p_num += 1

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
            respo = await self.async_get_req(
                url=_link,
                headers=self.headers
            )
            respo.encoding = 'utf-8'
            html_text = respo.text
            self.logger.info('Detail pageStart collecting %s', _link)

            pg_content = self.details_pg_parser(html_text=html_text, pg_data=pg_data)

            _title = re.sub(r'\s+', '', pg_data["title"])
            match = re.search(pattern, pg_content['title'])
            try:
                editor = match.group()
            except AttributeError:
                editor = ''
            detail_page_html_file = (
                    self.output_dir /
                    crawlers_categories[spider_name]['name'] /
                    f'''{pg_data['date']}/{_title}.html'''.replace('/', '')
            )
            self.save_html(
                html_content=html_text,
                file=detail_page_html_file
            )

            pg_content.update({key: pg_data[key] for key in ['link', 'date']})
            pg_content.update({'editor': editor})
            pg_content.update({'html_file': str(detail_page_html_file)})

        save_data(
            content=pg_content,
            file_path=(
                    self.output_dir /
                    crawlers_categories[spider_name]['name'] /
                    f"{self.start_date}/{self.end_date}-public-information.csv".replace('/','-')
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
        texts = html.xpath('//div[@class="article_l"]//text()')
        cleaned_texts = [clean_text(text) for text in texts]

        all_related_links = ''

        all_appendix = extract_related_links(html, xpath_query, _url_prefix)
        return {
            'text': '\n'.join(cleaned_texts).strip(),
            'appendix': ',\n'.join(all_appendix).replace('\xa0', ''),
            'related_documents': all_related_links,
            'title': title
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
            _page_date = ''.join(line.xpath('./span/text()')).strip()
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
                _title = ''.join(line.xpath('./a/text()')).strip()
                _link = ''.join(
                    line.xpath('./a/@href')
                ).strip().replace(
                    './',
                    f'''{'/'.join(self.page.url.split('/')[:-1])}/'''
                )
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
        spider_tasks = settings.NDRC_SPIDER
        for _s in spider_tasks:
            await self.get_public_info(spider_name=_s)
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
        f'{"".join(list(set(link.xpath(".//text()")))).strip()} {"".join(link.xpath("@href")).replace("./", f"""{prefix}/""")}'.strip()
        for
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
