"""
四川省人民政府
https://www.sc.gov.cn/10462/c102914/gfxwj.shtml	政府规范性文件
https://www.sc.gov.cn/10462/c103041/newzfwj.shtml 省政府政策文件
https://www.sc.gov.cn/10462/c111304/bmgfxwj.shtml?lion=1 政府信息公开
"""
import asyncio
from datetime import datetime
from pathlib import Path

from lxml import etree

from crawlers_tax_policy_data.config import settings
from crawlers_tax_policy_data.spider.base import BaseSpider
from crawlers_tax_policy_data.storage.local import save_data
from crawlers_tax_policy_data.utils.utils import clean_text

# gfxwj 规范文件 newzfwj 政策文件 bmgfxwj 政府信息公开
crawlers_category = {
    'gfxwj': 'c102914/gfxwj',
    'newzfwj': 'c103041/newzfwj.shtml',
    'bmgfxwj': 'c111304/bmgfxwj.shtml?lion=1'
}

crawlers_name = {
    'gfxwj': '规范文件',
    'newzfwj': '政策文件',
    'bmgfxwj': '政府信息公开'
}


class ScGovSpider(BaseSpider):
    """
    四川省人民政府 爬虫
    """

    def __init__(self):
        super().__init__()
        self.text_xpath = '//div[@class="info_cont word"]/p//span//text()'

    @property
    def url(self):
        """
        url
        :return:
        """
        return 'https://www.sc.gov.cn/10462/'

    @property
    def headers(self):
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": "yfx_c_g_u_id_10000001=_ck24042515112816087943581676676; yfx_f_l_v_t_10000001=f_t_1714029088600__r_t_1714029088600__v_t_1714029088600__r_c_0; _yfxkpy_ssid_10003074=%7B%22_yfxkpy_firsttime%22%3A%221714029088633%22%2C%22_yfxkpy_lasttime%22%3A%221714029088633%22%2C%22_yfxkpy_visittime%22%3A%221714029088633%22%2C%22_yfxkpy_domidgroup%22%3A%221714029088633%22%2C%22_yfxkpy_domallsize%22%3A%22100%22%2C%22_yfxkpy_cookie%22%3A%2220240425151128636721454305856448%22%7D; Hm_lvt_da7caec4897c6edeca8fe272db36cca4=1714029089; Hm_lpvt_da7caec4897c6edeca8fe272db36cca4=1714029536",
            "Host": "www.sc.gov.cn",
            "Referer": "https://www.sc.gov.cn/10462/c102914/gfxwj.shtml",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
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
            start_date = f'{check_date["start"].year}-{int(check_date["start"].month):02d}-{int(check_date["start"].day):02d}'
            end_date = f'{check_date["end"].year}-{int(check_date["end"].month):02d}-{int(check_date["end"].day):02d}'
        else:
            start_date = f'{check_date.year}-{int(check_date.month):02d}-{int(check_date.day):02d}'
            end_date = f'{check_date.year}-{int(check_date.month):02d}-{int(check_date.day):02d}'
        return start_date, end_date

    async def collect_data(self, name: str):
        """
        General method to collect data, parameterized to differentiate between GDI and ARRD.
        :param name:
        :return:
        """
        doc_type = crawlers_category[name]
        spider_name = crawlers_name[name]
        url = f'{self.url}{doc_type}.shtml'

        repo = await self.async_get_req(
            url=url,
            headers=self.headers
        )
        repo.encoding = 'utf-8'
        self.logger.info(repo)
        self.logger.info(f'Start collecting {spider_name} data at {url} for dates <{self.check_date}>')

        detail_pages = await self.parse_news_list(
            html_text=repo.text,
            spider_name=name,
            start_date=self.check_date[0],
            end_date=self.check_date[1]
        )

        if not detail_pages:
            self.logger.warning(f'No data found for {spider_name} at {url} for dates {self.check_date}')
            return

        for _p in detail_pages:
            _link = _p.get('link')
            output_folder = 'sc.gov.cn'
            await self.process_page(_p, output_folder)
        await self.stop_page()

    async def process_page(self, page_data, output_folder):
        """
        Process individual page and save data.
        :param page_data: Dictionary containing page details.
        :param output_folder: Output directory.
        :return:
        """
        _link = page_data.get('link')
        if 'pdf' in _link:
            content = {key: page_data[key] for key in ['link', 'date', 'title', 'editor']}
        else:
            await self.page.goto(_link)
            self.logger.info(f'Accessing detail page {_link}')
            content = await self.parse_detail_page()
            content.update({key: page_data[key] for key in ['link', 'date', 'title']})

        save_data(
            content=content,
            file_path=Path(
                settings.GOV_OUTPUT_PAHT) / output_folder / f"{self.check_date[0]}-{self.check_date[1]}-public-information.csv"
        )
        await asyncio.sleep(0.3)  # Controlled delay between requests

    async def get_gfxwj(self):
        """
        Get Government documents and interpretation
        """
        await self.collect_data('gfxwj')

    async def get_arrd(self):
        """
        Get Administrative Rules and Regulatory Documents
        """
        await self.collect_data(arrd=True)

    async def parse_news_list(self, html_text: str, spider_name: str, start_date: str, end_date: str):
        """
        parse news list
        :param spider_name:
        :param html_text:
        :param start_date:
        :param end_date:
        :return:
        """
        res = []
        html = etree.HTML(html_text, etree.HTMLParser(encoding="utf-8", remove_comments=False))

        def parse_news_items(all_row: list):
            """
            parse news items
            :param all_row:
            :return:
            """
            for row in all_row:
                _page_date = clean_text(''.join(row.xpath('./div[@class="lie4"]//text()')))
                _date = datetime.strptime(
                    _page_date,
                    '%Y-%m-%d'
                ).date()
                if (datetime.strptime(start_date, '%Y-%m-%d').date()
                        <= _date
                        <= datetime.strptime(end_date, '%Y-%m-%d').date()):
                    _title = clean_text(''.join(row.xpath('./div[@class="lie2"]/a/text()')))
                    _link = f'''https://www.sc.gov.cn{clean_text(''.join(row.xpath('./div[@class="lie2"]/a/@href')))}'''
                    _editor = clean_text(''.join(row.xpath('./div[@class="lie3"]//text()')))
                    res.append({
                        'title': _title,
                        'link': _link,
                        'date': _page_date,
                        'editor': _editor
                    })

        li_list = html.xpath('//div[@class="biaobody"]//li')
        parse_news_items(li_list)

        last_item_date_str = clean_text(''.join(li_list[-1].xpath('./div[@class="lie4"]//text()')))
        last_item_date = datetime.strptime(last_item_date_str, '%Y-%m-%d').date()

        doc_type = crawlers_category[spider_name]
        page_name = crawlers_name[spider_name]
        page_num = 2
        while last_item_date >= datetime.strptime(start_date, '%Y-%m-%d').date():
            _next_url = f'{self.url}{doc_type}_{page_num}.shtml'
            _repo = await self.async_get_req(_next_url)
            self.logger.info('get next page 四川省人民政府-%s %s', spider_name, _next_url)
            _repo.encoding = 'utf-8'

            next_html = etree.HTML(_repo.text, etree.HTMLParser(encoding="utf-8"))
            next_items_list = next_html.xpath('//div[@class="biaobody"]//li')
            parse_news_items(next_items_list)

            last_item_date_str = ''.join(next_items_list[-1].xpath('./div[@class="lie4"]//text()'))
            last_item_date = datetime.strptime(last_item_date_str, '%Y-%m-%d').date()
            page_num += 1

        return res

    async def parse_detail_page(self):
        """
        parse detail page


        :return:
        """
        res = {}
        self.logger.info('parse detail_page text data')

        file_xpath = self.build_file_xpath()
        xpath_query = f'//a[{file_xpath}]'

        html_text = await self.page.content()
        html = etree.HTML(
            html_text,
            etree.HTMLParser(encoding="utf-8")  # fix garbled characters in requests
        )
        file_status = self.extract_file_status(html)

        editor = next(
            (''.join(t.xpath('./text()')) for t in html.xpath('//table[@class="xxgk_table"]//td') if
             self.is_match(''.join(t.xpath('./text()'))))
        )

        all_related_links = self.extract_links(html, '//div[@class="right"]//a')

        all_appendix = self.extract_links(html, xpath_query)

        res.update({
            'text': clean_text(''.join(html.xpath('//div[@class="article"]/div[@class="left"]//p//text()'))),
            'related_documents': ','.join(all_related_links),
            'state': ''.join(file_status),
            'appendix': ','.join(all_appendix).replace('\xa0', ''),
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
        await self.get_gfxwj()
        # await self.get_arrd()
