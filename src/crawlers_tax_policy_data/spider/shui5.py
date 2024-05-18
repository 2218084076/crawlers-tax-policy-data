"""
税屋
https://www.shui5.cn/article/DiFangCaiShuiFaGui/ 税屋 > 地方法规
https://www.shui5.cn/article/NianDuCaiShuiFaGui/ 税屋 > 中央法规
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

pattern = re.compile(r'\S+[〔\[]\d{4}[〕\]]\d+号')

crawlers_categories = [
    {'name': '地方法规', 'suffix': 'DiFangCaiShuiFaGui'},
    {'name': '中央法规', 'suffix': 'NianDuCaiShuiFaGui'},
]


class ShuiWuSpider(BaseSpider):
    """
    国家发改委 spider
    """
    folder = '税屋'

    def __init__(self):
        super().__init__()
        self.start_date, self.end_date = self.check_date
        self.output_dir = Path(
            settings.GOV_OUTPUT_PAHT
        ) / self.folder / f'{self.start_date}-{self.end_date}'.replace('/', '')
        self.timestamp_format = '%Y-%m-%d'
        self.url_prefix = 'https://www.shui5.cn'

    @property
    def url(self):
        """
        url
        :return:
        """
        return 'https://www.shui5.cn/article/'

    @property
    def headers(self):
        """
        headers
        :return:
        """
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
                      "application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": "bdshare_ty=0x18; Hm_lvt_af9f35307710eaa56f112329ebc5d92c=1716020985; acw_tc=0a472f8c171603264385"
                      "23196e005837d7354d7c51c806a6aafe7b187601df; Hm_lpvt_af9f35307710eaa56f112329ebc5d92c=1716032644; "
                      "tfstk=flB-Ts4b5r4u-eVhFgNc8yywW8E0ITIzkaSsKeYoOZQAfGukOUXndJKMoTAHF7RBAabeK_v7Tq_vx3MBRYG5MDINkpb"
                      "dYu-BRw_p-_V0IgSyLpaMpR2G4CREz-BJd2jXtuy3OP2gIgsyLpagSkWexHRkAptWNYsbDHxnPpTWOoLXvhlIPw9QDiT2AXZz"
                      "2EoW2vBmIoKX0GYxdvnw2QT_QEHIdtK-SFsWbvMCH3dRKH6y2nOlOGRNEg2K3LjOGKtRRRaWhG1AjQB8WYYe9tQR9aqnTnCdA"
                      "OJyBDw5DLLJ1TdrYY71DM1MMtq_QLpWP6vPxcUlDTQl4tInAj9JEsdOedwZPefcX9KdLyyAWg11R6Iz1OXOIo3MWHc7DohETQ"
                      "tDVO7ez6iAMS-vSuOSTXRH0nLgDzGETQsvDFqS2Xle9kC..; ssxmod_itna=QqfhY5D5GIxGgxl8x+obxyix9DxRj6W6jPrQ"
                      "B1x05PreGzDAxn40iDtP=XmBegg0qx5o0A8BGseS0bmqaz8lm+5tiEA8TodDU4i8DCqcpWD4SKGwD0eG+DD4DW3qAoDexGPyn"
                      "LMKGWD4qDRDAQDzqQBDGfgDYPyiqDg/qDB+2dDKqGg+uxD0uxi1Gwxb02Sl4RxXeDSKAt3A0=DjdTD/+G8106o6PH5RLtHhpr"
                      "aiL04xBQD7kiyDYo0UeDH+kNKVOxAFY4slYxT7OD3bBGPGYmdKBDQY0qNWVMq4SDS27dU2yxDG+4rv0exD; ssxmod_itna2=Q"
                      "qfhY5D5GIxGgxl8x+obxyix9DxRj6W6jPrQBxnFSDa4Dso7DLig6QXpQjlSQqAP3clPnuQNPPbCgRmVC/fg0vx5brocjQ5/L30"
                      "wsXU=gWmb54/Qn2iqw9SSBp5eeyDBf2S/Cuw7kfURbTd9BRA/tb6xre0nzui5rWjqx453pCrpzT6p9kRl8ktpeCLQhCWqV4aNy"
                      "4NaoqUs/QfYyCIHwdypS2015SHCy+Gko90zwkw607BHS+Ys1zIs4KLvHpAwlRWEy99LgI0ue5N2EPBUhKWPdCn5PKC/0KunEnz"
                      "HwcFguNt3bxG2A04lig/24t0rbD4f2Ddyit74HBx1IxP2QehGbGqSxPzAP2BQYi4D08DiQ5BwtGb5lmPGxNGRQiDxD===",
            "Host": "www.shui5.cn",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
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

    async def get_public_info(self, crawlers: dict):
        """
        get public info
        :param crawlers:
        :return:
        """
        _url = f'{self.url}{crawlers["suffix"]}'

        self.logger.info(
            'Start collecting 税屋 %s %s %s-%s data',
            crawlers['name'], _url, self.start_date, self.end_date
        )

        await self.init_page()
        await self.page.goto(_url)
        await self.page.wait_for_timeout(350)
        await asyncio.sleep(0.5)

        detail_page_li = await self.list_page_parser()

        if not detail_page_li:
            self.logger.warning(
                'No data found for 税屋 %s %s for dates %s--%s', crawlers['name'], self.url, self.start_date,
                self.end_date
            )

        for pg in detail_page_li:
            await self.details_pg_processor(pg_data=pg, crawlers=crawlers)

    async def list_page_parser(self):
        """
        parse news list
        :return:
        """
        res = []
        html_text = await self.page.content()
        html: etree._Element = etree.HTML(html_text, etree.HTMLParser(encoding="utf-8"))

        nes_list: List[etree._Element] = html.xpath('//div[@class="left2c"]//div[@class="xwt2"]')
        res.extend(self.per_line_parser(nes_list))

        last_pg_date_str = ''.join(nes_list[-1].xpath('./div[@class="xwt2_d"]/p[@class="p3"]/text()')).strip()
        last_pg_date = datetime.strptime(last_pg_date_str, '%Y-%m-%d').date()

        while last_pg_date >= datetime.strptime(self.start_date, '%Y-%m-%d').date():
            # 下一页 click xpath
            # //div[@class="page"]//li[@class="cur"][last()]/a
            await self.page.locator('//div[@class="pagelist clearfix"]/a[position()=(last()-1)]').click()
            await self.page.wait_for_timeout(350)
            pg_num = await self.page.locator('//div[@class="pagelist clearfix"]/b/u').text_content()
            self.logger.info('next page is %s', pg_num)
            await asyncio.sleep(0.3)

            next_pg_text = await self.page.content()

            next_html: etree._Element = etree.HTML(
                next_pg_text,
                etree.HTMLParser(encoding="utf-8", remove_comments=False)
            )
            nex_lr_list: List[etree._Element] = next_html.xpath('//div[@class="left2c"]//div[@class="xwt2"]')
            res.extend(self.per_line_parser(nex_lr_list))

            _last_pg_date_str = ''.join(
                nex_lr_list[-1].xpath('./div[@class="xwt2_d"]/p[@class="p3"]/text()')
            ).strip()
            last_pg_date = datetime.strptime(_last_pg_date_str, '%Y-%m-%d').date()

        self.logger.info('There are %s proclamation items', len(res))
        return res

    async def details_pg_processor(self, pg_data: dict, crawlers: dict):
        """
        Detail page processor

        :param crawlers:
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
            detail_page_html_file = (
                    self.output_dir /
                    crawlers['name'] /
                    f'''{pg_data['date']}-{_title}.html'''.replace('/', '')
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
                    crawlers['name'] /
                    f"{self.start_date}-{self.end_date}-public-information.csv".replace('/', '-')
            )
        )
        await asyncio.sleep(0.5)

    def details_pg_parser(self, html_text: str, pg_data: dict):
        """
        details page parser

        :param pg_data:
        :param html_text:
        :return:
        """
        _url_prefix = '/'.join(pg_data['link'].split('/')[:3])

        file_xpath = self.build_file_xpath()
        xpath_query = f'//a[{file_xpath}]'

        html = etree.HTML(
            html_text,
            etree.HTMLParser(encoding="utf-8")  # fix garbled characters in requests
        )
        title = ''.join(html.xpath('//div[@class="articleTitle"]//text()')).strip()
        texts = html.xpath('//div[@class="main2"]/div[@class="left2"]//p//text()')
        cleaned_texts = [clean_text(text) for text in texts]

        all_related_links = []
        for p in html.xpath('//div[@class="left2i"]//a'):
            _title = ''.join(p.xpath('./text()'))
            _link = ''.join(p.xpath('./@href'))
            all_related_links.append(f'''{_title} {_link}''')

        all_appendix = extract_related_links(html, xpath_query, _url_prefix)
        return {
            'text': '\n'.join(cleaned_texts).replace('\r\n\n', '\r\n').strip(),
            'appendix': ',\n'.join(all_appendix).replace('\xa0', ''),
            'related_documents': ',\n'.join(all_related_links),
            'title': title,
            'editor': ''.join([
                item.strip() for item in html.xpath('//div[@id="tupain"]//p[@style="text-align: center;"]//text()') if
                pattern.search(item)
            ])
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
            _page_date = ''.join(line.xpath('./div[@class="xwt2_d"]/p[@class="p3"]/text()')).strip()
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
                _title = ''.join(line.xpath('./div[@class="xwt2_a"]/a/text()')).strip()
                _link = ''.join(
                    line.xpath('./div[@class="xwt2_a"]/a/@href')
                ).strip()
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
        for crawler in crawlers_categories:
            await self.get_public_info(crawler)
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
        f'{"".join(list(set(link.xpath(".//text()")))).strip()}  {prefix}{"".join(link.xpath("@href"))}'.strip()
        for
        link in
        html.xpath(xpath)
    ]
