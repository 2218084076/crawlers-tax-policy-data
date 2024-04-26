"""
江苏省人民政府 > 政府文件及解读
              > 规章行政规范性文件
http://www.jiangsu.gov.cn/col/col76841/index.html
http://www.jiangsu.gov.cn/col/col76556/index.html > http://www.jiangsu.gov.cn/col/col76705/index.html
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


class JsGovSpider(BaseSpider):
    """
    广州市行政规范性文件统一发布平台 爬虫
    """
    folder = 'jiangsu.gov.cn'

    def __init__(self):
        super().__init__()
        self.text_xpath = '//div[@class="info_cont word"]/p//span//text()'

    @property
    def url(self):
        """
        url
        :return:
        """
        return 'http://www.jiangsu.gov.cn/col/'

    @property
    def headers(self):
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": "__jsluid_h=39756ea1fafaa02d0b3a03353fe0d282; zh_choose_1=s; arialoadData=true; ariawapChangeViewPort=false; d7d579b9-386c-482a-b971-92cad6721901=WyI0MjIyMDUwNDUiXQ",
            "Host": "www.jiangsu.gov.cn",
            "If-Modified-Since": "Thu, 01 Feb 2024 03:54:02 GMT",
            "If-None-Match": "W/\"65bb15da-39f6\"",
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

    async def collect_data(self, arrd=False):
        """
        General method to collect data, parameterized to differentiate between GDI and ARRD.
        :param arrd: Boolean, if True it handles ARRD, else handles GDI.
        :return:
        """
        doc_type = 'ARRD' if arrd else 'GDI'
        col_index = 'col76705' if arrd else 'col76841'
        url = f'{self.url}{col_index}/index.html'

        await self.init_page()
        await self.page.goto(url)
        await self.page.wait_for_timeout(400)
        self.logger.info(f'Start collecting {doc_type} data at {url} for dates <{self.check_date}>')

        detail_pages = await self.parse_news_list(start_date=self.check_date[0], end_date=self.check_date[1])

        if not detail_pages:
            self.logger.warning(f'No data found for {doc_type} at {url} for dates {self.check_date}')
            return

        for _p in detail_pages:
            _link = _p.get('link')
            output_folder = 'jiangsu.gov.cn' if 'pdf' in _link else 'jiangsu.gov.cn'
            await self.process_page(_p)
        await self.stop_page()

    async def process_page(self, page_data):
        """
        Process individual page and save data.
        :param page_data: Dictionary containing page details.
        :return:
        """
        start_date, end_date = self.check_date

        _link = page_data.get('link')
        if 'pdf' in _link:
            content = {key: page_data[key] for key in ['link', 'date', 'title']}
        else:
            await self.page.goto(_link)
            html_text = await self.page.content()
            content = self.parse_detail_page(html_text)

            _title = re.sub(r'\s+', '', page_data["title"])
            detail_page_html_file = Path(
                settings.GOV_OUTPUT_PAHT
            ) / self.folder / f'{start_date}-{end_date}' / f'''{page_data['date']}-{_title}.html'''
            self.save_html(
                html_content=html_text,
                file=detail_page_html_file
            )
            content.update({key: page_data[key] for key in ['link', 'date', 'title']})
            content.update({'html_file': str(detail_page_html_file)})

        save_data(
            content=content,
            file_path=Path(
                settings.GOV_OUTPUT_PAHT) / self.folder / f"{start_date}-{end_date}" / f"{self.check_date[0]}-{self.check_date[1]}-public-information.csv"
        )
        await asyncio.sleep(0.3)

    async def get_gdi(self):
        """
        Get Government documents and interpretation
        """
        await self.collect_data(arrd=False)

    async def get_arrd(self):
        """
        Get Administrative Rules and Regulatory Documents
        """
        await self.collect_data(arrd=True)

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
                _page_date = clean_text(''.join(row.xpath('./b/text()')))
                _date = datetime.strptime(
                    _page_date,
                    '%Y-%m-%d'
                ).date()
                if (datetime.strptime(start_date, '%Y-%m-%d').date()
                        <= _date
                        <= datetime.strptime(end_date, '%Y-%m-%d').date()):
                    _title = clean_text(''.join(row.xpath('./a/text()')))
                    _link = clean_text(''.join(row.xpath('./a/@href')))
                    res.append({'title': _title, 'link': _link, 'date': _page_date})

        li_list = html.xpath('//ul[@id="gz_list"]//li')
        parse_news_items(li_list)

        last_item_date_str = clean_text(''.join(li_list[-1].xpath('./b/text()')))
        last_item_date = datetime.strptime(last_item_date_str, '%Y-%m-%d').date()

        while last_item_date >= datetime.strptime(start_date, '%Y-%m-%d').date():
            await self.page.locator('//a[@title="下一页"]').click()
            await self.page.wait_for_timeout(350)
            next_html_text = await self.page.content()
            next_html = etree.HTML(next_html_text, etree.HTMLParser(encoding="utf-8"))
            next_items_list = next_html.xpath('//ul[@id="gz_list"]//li')
            parse_news_items(next_items_list)

            last_item_date_str = ''.join(next_items_list[-1].xpath('./b/text()'))
            last_item_date = datetime.strptime(last_item_date_str, '%Y-%m-%d').date()

        return res

    def parse_detail_page(self, html_text):
        """
        parse detail page


        :return:
        """
        res = {}
        self.logger.info('parse detail_page text data')

        file_xpath = self.build_file_xpath()
        xpath_query = f'//a[{file_xpath}]'

        html = etree.HTML(
            html_text,
            etree.HTMLParser(encoding="utf-8")  # fix garbled characters in requests
        )

        file_status = self.extract_file_status(html)
        texts = html.xpath('//div[@class="article"]/div[@class="left"]//p//text()')
        cleaned_texts = [clean_text(text) for text in texts]

        editor = next(
            (''.join(t.xpath('./text()')) for t in html.xpath('//table[@class="xxgk_table"]//td') if
             self.is_match(''.join(t.xpath('./text()'))))
        )

        all_related_links = self.extract_links(html, '//div[@class="right"]//a')

        all_appendix = self.extract_links(html, xpath_query)

        res.update({
            'text': '\n'.join(cleaned_texts).strip(),
            'related_documents': ',\n'.join(all_related_links),
            'state': ''.join(file_status),
            'appendix': ',\n'.join(all_appendix).replace('\xa0', ''),
            'editor': editor
        })

        return res

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

    def extract_page_text(self, html):
        return clean_text(' '.join(html.xpath(self.text_xpath)))

    @staticmethod
    def extract_file_status(html):
        """
        Extract bulletin status
        :param html:
        :return:
        """
        for i in html.xpath('//table[@class="xxgk_table"]//td'):
            if clean_text(''.join(i.xpath('./text()'))) == "时 效：":
                next_td_text = ''.join(i.xpath('following-sibling::td[1]/text()'))
                return next_td_text
        return ''

    @staticmethod
    def extract_links(html, xpath):
        """
        Extract the links according to the given XPath
        :param html:
        :param xpath:
        :return:
        """
        return [f'{"".join(link.xpath("./text()"))} http://www.jiangsu.gov.cn{"".join(link.xpath("@href"))}' for link in
                html.xpath(xpath)]

    async def run(self):
        """
        run crawlers
        :return:
        """
        self.logger.info('start running crawlers...')
        await self.get_gdi()
        await self.get_arrd()
