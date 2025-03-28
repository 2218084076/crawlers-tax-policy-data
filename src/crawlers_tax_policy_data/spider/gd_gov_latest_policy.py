"""
广东省人民政府
`首页 > 要闻动态 > 政务专题 > 聚焦粤港澳大湾区建设发展 > 最新政策 ` 数据采集
http://www.gd.gov.cn/gdywdt/zwzt/ygadwq/zxzc/index.html
"""
import asyncio
import re
from datetime import datetime
from pathlib import Path

from lxml import etree

from crawlers_tax_policy_data.config import settings
from crawlers_tax_policy_data.spider.base import BaseSpider
from crawlers_tax_policy_data.storage.local import save_data
from crawlers_tax_policy_data.utils.utils import clean_text, pattern


class GdGovLatestPolicySpider(BaseSpider):
    """
    广东省人民政府 `首页 > 要闻动态 > 政务专题 > 聚焦粤港澳大湾区建设发展 > 最新政策` 数据采集
    """
    folder = 'gd.gov.cn'

    def __init__(self):
        super().__init__()
        self.file_types = ['.pdf', '.xls', '.xlsx', '.doc', '.docx', '.ppt', '.pptx', '.txt', '.odt', '.wps', '.jpg']

    @property
    def url(self):
        """
        url
        :return:
        """
        return 'http://www.gd.gov.cn/gdywdt/zwzt/ygadwq/zxzc/index.html?version=slh'

    @property
    def headers(self):
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": "aliyungf_tc=66e137911b747a9a423eee37f229d5044c8193f8d7290f1994f5040df8e1167a; ZJZWFWSESSIONID=3c684f7c-cee2-4ff9-a6bf-7cdcfc38041a; zh_choose_undefined=s; arialoadData=false; cssstyle=1; acw_tc=ac11000117138618692624485eb1b1da04ae65b2c8bfc00566a616c3f60472; SERVERID=bc6beea6e995cecb42c7a1341ba3517f|1713862061|1713859772",
            "If-Modified-Since": "Fri, 12 Apr 2024 08:19:29 GMT",
            "If-None-Match": "W/\"6618ee91-6adb\"",
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

    async def get_public_info(self):
        """
        get public information
        :return:
        """
        start_date, end_date = self.check_date
        self.logger.info('Start collecting %s %s-%s data', '广东省人民政府 > 最新政策', start_date, end_date)
        await self.init_page()
        await self.page.goto(self.url)
        self.logger.info('get %s', self.page)
        detail_pages = await self.parse_news_list(start_date=start_date, end_date=end_date)

        if not detail_pages:
            self.logger.warning('广东省人民政府 > 最新政策 <%s> no data', (start_date, end_date))
            return ''

        for _p in detail_pages:
            _link = _p.get('link')
            if 'pdf' in _link:
                save_data(
                    content={'link': _link, 'date': _p['date'], 'title': _p['title']},
                    file_path=Path(
                        settings.GOV_OUTPUT_PAHT) / self.folder / f'{start_date}-{end_date}' / 'Latest policy' / f'{start_date}-{end_date}-public'
                                                                                                                 f'-information.csv'
                )
            else:
                await self.init_page()
                await self.page.goto(_link)
                html_text = await self.page.content()
                detail_data = self.parse_detail_page(html_text)

                _title = re.sub(r'\s+', '', detail_data["title"])
                detail_page_html_file = Path(
                    settings.GOV_OUTPUT_PAHT
                ) / self.folder / f'{start_date}-{end_date}' / 'Latest policy' / f'''{_p['date']}-{_title}.html'''
                self.save_html(
                    html_content=html_text,
                    file=detail_page_html_file
                )

                detail_data.update({
                    'link': _link,
                    'date': _p['date'],
                    'html_file': str(detail_page_html_file)
                })

                save_data(
                    content=detail_data,
                    file_path=Path(
                        settings.GOV_OUTPUT_PAHT) / self.folder / f'{start_date}-{end_date}' / 'Latest policy' / f'{start_date}-{end_date}-public'
                                                                                                                 f'-information.csv'
                )
                await asyncio.sleep(0.5)
        await self.stop_page()

    async def parse_news_list(self, start_date: str, end_date: str):
        """
        parse news list
        :param start_date:
        :param end_date:
        :return:
        """
        res = []
        html_text = await self.page.content()
        html = etree.HTML(html_text, etree.HTMLParser(encoding="utf-8"))

        def parse_news_items(all_row: list):
            """
            parse news items
            :param all_row:
            :return:
            """
            for row in all_row:
                _page_date = clean_text(''.join(row.xpath('./span[3]/text()')))
                _date = datetime.strptime(
                    _page_date,
                    '%Y-%m-%d'
                ).date()
                if (datetime.strptime(start_date, '%Y-%m-%d').date()
                        <= _date
                        <= datetime.strptime(end_date, '%Y-%m-%d').date()
                ):
                    _title = clean_text(''.join(row.xpath('./span/a/text()')))
                    _link = clean_text(''.join(row.xpath('./span/a/@href')))
                    res.append({'title': _title, 'link': _link, 'date': _page_date})

        items_list = html.xpath('//div[@class="viewList"]/ul//li')[1:]
        parse_news_items(items_list)

        last_item_date_str = clean_text(''.join(items_list[-1].xpath('./span[3]/text()')))
        last_item_date = datetime.strptime(last_item_date_str, '%Y-%m-%d').date()

        while last_item_date >= datetime.strptime(start_date, '%Y-%m-%d').date():
            await self.page.locator('//a[@class="next"]').click()
            await self.page.wait_for_timeout(400)
            page_text = await self.page.content()
            next_html = etree.HTML(page_text, etree.HTMLParser(encoding="utf-8"))
            next_items_list = next_html.xpath('//div[@class="viewList"]/ul//li')[1:]
            parse_news_items(next_items_list)

            last_item_date_str = ''.join(next_items_list[-1].xpath('./span[3]/text()'))
            last_item_date = datetime.strptime(last_item_date_str, '%Y-%m-%d').date()

        await self.stop_page()
        return res

    def parse_detail_page(self, html_text: str):
        """
        parse detail page
        :param html_text:
        :return:
        """
        res = {}
        file_xpath = self.build_file_xpath()
        xpath_query = f'//div[@class="zw"]//a[{file_xpath}]'
        html = etree.HTML(
            html_text,
            etree.HTMLParser(encoding="utf-8")  # fix garbled characters in requests
        )
        title = ''.join(html.xpath('//div[@class="viewList"]/h3/text()')).strip()
        # 文号
        editor = next((
            i.text.strip() for i in html.xpath('//div[@wzades="正文"]//p') if
            i.text and re.match(pattern, i.text.strip())), ''
        )
        all_appendix = self.extract_links(html, xpath_query)
        for img in html.xpath('//div[@class="zw"]//img'):
            alt = img.xpath('./@alt')
            _img_link = img.xpath('./@src')
            all_appendix.append(f'{"".join(alt)}-{"".join(_img_link)}')

        related_documents = ',\n'.join(html.xpath('//span[@class="ly"]/text()')).strip()
        res.update({
            'title': title,
            'text': title + clean_text('\n'.join(html.xpath('//div[@wzades="正文"]//p//text()'))),
            'editor': editor,
            'appendix': ',\n'.join(all_appendix).replace('\xa0', ''),
            'related_documents': related_documents,
        })

        return res

    async def run(self):
        """
        run crawlers
        :return:
        """
        self.logger.info('start running crawlers...')
        await self.get_public_info()
