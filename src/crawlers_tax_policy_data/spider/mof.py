"""
财政部
http://www.mof.gov.cn/gkml/caizhengwengao/ 财政文告
http://www.mof.gov.cn/gkml/bulinggonggao/czbl/ 财政部令
http://www.mof.gov.cn/gkml/bulinggonggao/czbgg/ 财政部公告
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

url_suffix = settings.MOF_URL_SUFFIX


# url_suffix = {
#     '财政文告': '/caizhengwengao/index',  # 财政文告
#     '财政部令': '/bulinggonggao/czbl/index',  # 财政部令
#     '财政部公告': '/bulinggonggao/czbgg/index'  # 财政部公告
# }


class MofSpider(BaseSpider):
    """
    财政部 spider
    """
    folder = 'mof.gov.cn'

    def __init__(self):
        super().__init__()
        self.start_date, self.end_date = self.check_date
        self.timestamp_format = '%Y-%m-%d'
        self.url_prefix = 'https://www.mof.gov.cn/gkml/caizhengwengao/'
        self.spider_name = ''

    @property
    def output_dir(self):
        return Path(
            settings.GOV_OUTPUT_PAHT
        ) / self.folder / self.spider_name / f'{self.start_date}-{self.end_date}'

    @property
    def url(self):
        """
        url

        url prefix
        # 财政文告 `url prefix` + `/caizhengwengao/index`
        # 财政部令 `url prefix` + `/bulinggonggao/czbl/`
        # 财政部公告 `url prefix` + `bulinggonggao/czbgg/`
        :return:
        """
        return 'http://www.mof.gov.cn/gkml'

    @property
    def headers(self):
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Cookie": "HMF_CI=f119287b6f50e0d960bc5221b21120c579b756b295f40011fde3714358d3ca3080a16af9467e0ef3551b12e6b8f6c4b3f32a4149bf2df56d1cd082b7b824389b07; HMY_JC=82a4dbc28c2fe213f1cf2283672caf627c61dfb77c05d85778db7b0d6436ebcc75,; HBB_HC=03c39cb28d4c7cb36eca2504df763ca6193f553622c95b6288ebf23409f2a5c45b1e9eca667e537d78fc571ca8cff4f5ba",
            "Host": "www.mof.gov.cn",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
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

    async def get_public_info(self, suffix: str):
        """
        get public information
        :param spider_name:
        :param suffix:
        :return:
        """
        _url = f'{self.url}{suffix}.htm'
        self.logger.info(
            'Start collecting 财政部-%s %s %s-%s data',
            self.spider_name, _url, self.start_date, self.end_date
        )

        repo = await self.async_get_req(
            url=_url,
            headers=self.headers
        )
        repo.encoding = 'utf-8'
        html_text = repo.text
        detail_page_li = await self.list_page_parser(
            html_text=html_text,
            suffix=suffix
        )

        if not detail_page_li:
            self.logger.warning(
                f'No data found for 财政部-%s %s for dates %s-%s',
                self.spider_name, self.url, self.start_date, self.end_date
            )
        _n = 1
        for pg in detail_page_li:
            await self.details_pg_processor(pg_data=pg)
            self.logger.info('page %s', _n)
            _n += 1

    async def list_page_parser(self, html_text: str, suffix: str):
        """
        parse news list
        :param suffix:
        :param html_text:
        :return:
        """
        p_num = 2
        if self.spider_name == '财政部公告':
            p_num = 1
        res = []
        html = etree.HTML(html_text, etree.HTMLParser(encoding="utf-8"))

        li_list: List[etree._Element] = html.xpath('//ul[@class="xwbd_lianbolistfrcon"]//li')
        res.extend(self.per_line_parser(li_list))

        last_pg_date_str = ''.join(li_list[-1].xpath('./span/text()')).strip()
        last_pg_date = datetime.strptime(last_pg_date_str, '%Y-%m-%d').date()
        while last_pg_date >= datetime.strptime(self.start_date, '%Y-%m-%d').date():
            _url = f'{self.url}{suffix}_{p_num}.htm'

            _repo = await self.async_get_req(
                url=_url,
                headers=self.headers
            )
            _repo.encoding = 'utf-8'
            next_pg_text = _repo.text

            next_html: etree._Element = etree.HTML(
                next_pg_text,
                etree.HTMLParser(encoding="utf-8", remove_comments=False)
            )
            nex_li_list: List[etree._Element] = next_html.xpath('//ul[@class="xwbd_lianbolistfrcon"]//li')
            res.extend(self.per_line_parser(nex_li_list))

            _last_pg_date_str = ''.join(nex_li_list[-1].xpath('./span/text()')).strip()
            last_pg_date = datetime.strptime(_last_pg_date_str, '%Y-%m-%d').date()
            p_num += 1
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

            pg_content = self.details_pg_parser(html_text=html_text, pg_url=_link)

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
            pg_url: str
    ):
        """
        details page parser

        :param pg_url:
        :param html_text:
        :return:
        """
        _url_prefix = f"{'/'.join(pg_url.split('/')[:-1])}/"
        if self.spider_name == '财政文告':
            _url_prefix = 'https://www.safe.gov.cn'

        file_xpath = self.build_file_xpath()
        xpath_query = f'//a[{file_xpath}]'

        html: etree._Element = etree.HTML(
            html_text,
            etree.HTMLParser(encoding="utf-8")  # fix garbled characters in requests
        )
        title = ''.join(html.xpath('//meta[@name="ArticleTitle"]/@content')).strip()

        texts = html.xpath('//div[@class="TRS_Editor"]//*[not(self::style)]/text()')
        cleaned_texts = [clean_text(text) for text in texts]
        editor = [i for i in texts if self.is_match(i.strip())]

        all_related_links = [
            f'''{"".join(list(set(link.xpath(".//text()"))))} {"".join(link.xpath("@href")).replace("./", _url_prefix)}'''.strip()
            for link in html.xpath('//ul[@id="down"]//a')
        ]

        all_appendix = extract_related_links(html, xpath_query, _url_prefix)
        all_appendix.extend([
            f'''{"".join(link.xpath("@src")).replace('./', _url_prefix)}'''.strip()
            for link in html.xpath('//div[@class="TRS_Editor"]//p//img')
        ])
        return {
            'title': title,
            'text': '\n'.join(cleaned_texts).strip(),
            'editor': ''.join(editor).strip(),
            'appendix': ',\n'.join(all_appendix).replace('\xa0', '').strip(),
            'related_documents': ',\n'.join(list(set(all_related_links))).strip(),
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
        prefix = ''
        if self.spider_name == '财政文告':
            prefix = self.url_prefix

        for line in li_list_html:
            _page_date = ''.join(line.xpath('./span/text()')).strip()
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
                _link = ''.join(line.xpath('.//a/@href')).strip()
                if prefix:
                    _link = ''.join(line.xpath('.//a/@href')).strip().replace('./', prefix)

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
        for k, v in url_suffix.items():
            self.spider_name = k
            await self.get_public_info(suffix=v)
            await asyncio.sleep(2)


def extract_related_links(html, xpath, prefix: str):
    """
    Extract the links according to the given XPath
    :param prefix:
    :param html:
    :param xpath:
    :return:
    """
    if prefix:
        return [
            f'{"".join(list(set(link.xpath(".//text()"))))} {"".join(link.xpath("@href")).replace("./", prefix)}'.strip()
            for link in html.xpath(xpath)
        ]
    return [
        f'{"".join(list(set(link.xpath(".//text()"))))} {prefix}{"".join(link.xpath("@href"))}'.strip()
        for link in html.xpath(xpath)
    ]
