"""
广州市行政规范性文件统一发布平台
https://www.gz.gov.cn/gfxwj/
"""
import asyncio
import re
from datetime import datetime
from pathlib import Path

from lxml import etree

from crawlers_tax_policy_data.config import settings
from crawlers_tax_policy_data.spider.base import BaseSpider
from crawlers_tax_policy_data.storage.local import save_data
from crawlers_tax_policy_data.utils.utils import clean_text


class GzGovSpider(BaseSpider):
    """
    广州市行政规范性文件统一发布平台 爬虫
    """
    folder = 'gz.gov.cn'

    def __init__(self):
        super().__init__()
        self.status_xpath = '//span[@id="file_status"]/following-sibling::text()'
        self.title_xpath = '//h1[@class="info_title"]/text()'
        self.text_xpath = '//div[@class="info_cont word"]/p//span//text()'

    @property
    def url(self):
        """
        url
        :return:
        """
        return 'https://www.gz.gov.cn/gfxwj/'

    @property
    def headers(self):
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
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
            start_date = f'{check_date["start"].year}年{int(check_date["start"].month):02d}月{int(check_date["start"].day):02d}日'
            end_date = f'{check_date["end"].year}年{int(check_date["end"].month):02d}月{int(check_date["end"].day):02d}日'
        else:
            start_date = f'{check_date.year}年{int(check_date.month):02d}月{int(check_date.day):02d}日'
            end_date = f'{check_date.year}年{int(check_date.month):02d}月{int(check_date.day):02d}日'
        return start_date, end_date

    async def get_public_info(self):
        """
        get public information
        :return:
        """
        start_date, end_date = self.check_date
        self.logger.info(
            'Start collecting 广州市行政规范性文件统一发布平台 %s %s-%s data', self.url, start_date, end_date
        )
        await self.init_page()
        await self.page.goto(self.url)
        await self.page.wait_for_timeout(400)
        detail_pages = await self.parse_news_list(start_date=start_date, end_date=end_date)

        if not detail_pages:
            self.logger.warning('广州市行政规范性文件统一发布平台  <%s> no data', (start_date, end_date))
            return ''

        for _p in detail_pages:
            _link = _p.get('link')
            if 'pdf' in _link:
                save_data(
                    content={'link': _link, 'date': _p['date'], 'title': _p['title'], 'editor': _p['editor']},
                    file_path=Path(
                        settings.GOV_OUTPUT_PAHT) / self.folder / f'{start_date}-{end_date}' / f'{start_date}-{end_date}-public'
                                                                                               f'-information.csv'
                )
            else:
                await self.page.goto(_link)
                html_text = await self.page.content()

                detail_data = await self.parse_detail_page(html_text)

                _title = re.sub(r'\s+', '', detail_data["title"])
                detail_page_html_file = Path(
                    settings.GOV_OUTPUT_PAHT
                ) / self.folder / f'{start_date}-{end_date}' / f'''{_p['date']}-{_title}.html'''
                self.save_html(
                    html_content=html_text,
                    file=detail_page_html_file
                )

                detail_data.update({
                    'link': _link,
                    'date': _p['date'],
                    'editor': _p['editor'],
                    'html_file': str(detail_page_html_file)
                })

                save_data(
                    content=detail_data,
                    file_path=Path(
                        settings.GOV_OUTPUT_PAHT) / self.folder / f'{start_date}-{end_date}' / f'{start_date}-{end_date}-public-information.csv'
                )
                await asyncio.sleep(0.3)
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
                _page_date = clean_text(''.join(row.xpath('./td[@class="hide"][2]/text()')))
                _date = datetime.strptime(
                    _page_date,
                    '%Y年%m月%d日'
                ).date()
                if (datetime.strptime(start_date, '%Y年%m月%d日').date()
                        <= _date
                        <= datetime.strptime(end_date, '%Y年%m月%d日').date()):
                    _title = clean_text(''.join(row.xpath('./td[2]/a/text()')))
                    _link = clean_text(''.join(row.xpath('./td[2]/a/@href')))
                    _editor = clean_text(''.join(row.xpath('./td[@class="hide"][1]/text()')))
                    res.append({'title': _title, 'link': _link, 'date': _page_date, 'editor': _editor})

        lr_list = html.xpath('//table[@id="bbsTab"]//tr')[1:]
        parse_news_items(lr_list)

        last_item_date_str = clean_text(''.join(lr_list[-1].xpath('./td[@class="hide"][2]/text()')))
        last_item_date = datetime.strptime(last_item_date_str, '%Y年%m月%d日').date()

        while last_item_date >= datetime.strptime(start_date, '%Y年%m月%d日').date():
            await self.page.locator('//a[@id="next"]').click()
            await self.page.wait_for_timeout(350)
            next_html_text = await self.page.content()
            next_html = etree.HTML(next_html_text, etree.HTMLParser(encoding="utf-8"))
            next_items_list = next_html.xpath('//table[@id="bbsTab"]//tr')[1:]
            parse_news_items(next_items_list)

            last_item_date_str = ''.join(next_items_list[-1].xpath('./td[@class="hide"][2]/text()'))
            last_item_date = datetime.strptime(last_item_date_str, '%Y年%m月%d日').date()

        return res

    async def parse_detail_page(self, html_text: str):
        """
        parse detail page


        :return:
        """
        res = {}
        self.logger.info('parse detail_page text data')

        file_xpath = self.build_file_xpath()
        xpath_query = f'//a[{file_xpath}]'

        await self.handle_page_js()
        html = etree.HTML(
            html_text,
            etree.HTMLParser(encoding="utf-8")  # fix garbled characters in requests
        )

        file_status = self.extract_file_status(html)
        title = self.extract_title(html)
        texts = html.xpath('//div[@id="info_cont"]//text()')
        cleaned_texts = [clean_text(text) for text in texts]
        all_related_links = self.extract_links(html, '//table[@id="bbsTab"]//a')

        all_appendix = self.extract_links(html, xpath_query)

        res.update({
            'title': title,
            'text': title + '\n'.join(cleaned_texts),
            'related_documents': ',\n'.join(all_related_links),
            'state': ''.join(file_status).strip(),
            'appendix': ',\n'.join(all_appendix).replace('\xa0', '')
        })

        return res

    def build_file_xpath(self):
        """
        Generate an XPath query string based on a list of file types
        :return:
        """
        return " or ".join(
            [f"substring(@href, string-length(@href) - string-length('{ft}') + 1) = '{ft}'" for ft in self.file_types]
        )

    async def handle_page_js(self):
        """
        在页面上执行JavaScript以处理文件状态。
        """
        js_code = """
        var todayTimeStamp = new Date(new Date().setHours(0, 0, 0, 0)) / 1000;
        var tTimeStamp = todayTimeStamp;
        var losetime = '1715270400';
        var file_status = '尚未施行';
        if(losetime == null ||losetime==""){
            losetime = '';
        }
        if(file_status == null ||file_status==""){
            file_status = '';
        }
        if(file_status!= null || file_status != ""){
            $('#file_status').parent().append(file_status);
        }else if(losetime == null || losetime == "" || losetime == 0 || losetime < tTimeStamp){
            $('#file_status').parent().append("失效");
        }else{
            $('#file_status').parent().append("有效");
        }
        """
        await self.page.evaluate(js_code)

    def extract_title(self, html):
        """
        Extract page title
        :param html:
        :return:
        """
        return clean_text(''.join(html.xpath(self.title_xpath)))

    @staticmethod
    def extract_links(html, xpath):
        """
        Extract the links according to the given XPath
        :param html:
        :param xpath:
        :return:
        """
        return [''.join(link.xpath('./text()')) + ' ' + ''.join(link.xpath('@href')) for link in html.xpath(xpath)]

    def extract_page_text(self, html):
        return clean_text(' '.join(html.xpath(self.text_xpath)))

    def extract_file_status(self, html):
        """
        Extract bulletin status
        :param html:
        :return:
        """
        status_text = ''.join(html.xpath(self.status_xpath))
        return set(clean_text(status_text).split())

    async def run(self):
        """
        run crawlers
        :return:
        """
        self.logger.info('start running crawlers...')
        await self.get_public_info()
