"""
四川省人民政府
https://www.sc.gov.cn/10462/c102914/gfxwj.shtml	政府规范性文件
https://www.sc.gov.cn/10462/c103041/newzfwj.shtml 省政府政策文件
https://www.sc.gov.cn/10462/c111304/bmgfxwj.shtml?lion=1 政府信息公开
"""
import asyncio
import re
from datetime import datetime
from pathlib import Path

from lxml import etree

from crawlers_tax_policy_data.config import settings
from crawlers_tax_policy_data.spider.base import BaseSpider
from crawlers_tax_policy_data.spider.sc_newzfwj import ScNewzfwj
from crawlers_tax_policy_data.storage.local import save_data
from crawlers_tax_policy_data.utils.utils import clean_text

# gfxwj 规范文件 newzfwj 政策文件 bmgfxwj 政府信息公开
crawlers_category = {
    'gfxwj': 'c102914/gfxwj',
    'newzfwj': 'https://www.sc.gov.cn/10462/c103041/newzfwj.shtml?channelid=9c2314405df140af83649dff8f30055b&keyWord=&wh=&title=&fwzh=&pageSize=15&pageNum=',
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
    folder = 'sc.gov.cn/政府规范性文件'

    def __init__(self):
        super().__init__()
        self.text_xpath = '//div[@class="info_cont word"]/p//span//text()'
        self.newzfwj_spider = ScNewzfwj()

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
        start_date, end_date = self.check_date

        doc_type = crawlers_category[name]
        spider_name = crawlers_name[name]
        url = f'{self.url}{doc_type}.shtml'

        repo = await self.async_get_req(
            url=url,
            headers=self.headers
        )
        repo.encoding = 'utf-8'
        self.logger.info(
            f'Start collecting `四川省人民政府 %s` data at %s for dates %s-%s',
            spider_name,
            url,
            start_date,
            end_date
        )
        detail_pages = await self.parse_news_list(
            html_text=repo.text,
            spider_name=name,
            start_date=start_date,
            end_date=end_date
        )

        if not detail_pages:
            self.logger.warning(f'No data found for %s at %s for dates %s-%s', spider_name, url, start_date, end_date)
            return []

        await self.init_page()
        for _p in detail_pages:
            await self.process_page(_p, start_date, end_date)

        await self.stop_page()

    async def process_page(self, page_data, start_date, end_date):
        """
        Process individual page and save data.
        :param start_date:
        :param end_date:
        :param page_data: Dictionary containing page details.
        :return:
        """
        _link = page_data.get('link')

        if 'pdf' in _link:
            content = {key: page_data[key] for key in ['link', 'date', 'title', 'editor']}
        else:
            await self.page.goto(_link)
            await self.page.wait_for_timeout(350)
            # repo = await self.async_get_req(url=_link, headers=self.headers)
            # repo.encoding = 'utf-8'
            html_text = await self.page.content()
            content = await self.parse_detail_page(html_text=html_text)

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
                settings.GOV_OUTPUT_PAHT) / self.folder / f'{start_date}-{end_date}' / f"{start_date}-{end_date}-public-information.csv"
        )
        await asyncio.sleep(0.3)

    async def get_gfxwj(self):
        """
        Get Government documents and interpretation
        """
        await self.collect_data('gfxwj')

    async def get_newzfwj(self):
        """
        Collect data from the "Provincial Government Policy Documents" section of the website
        :return:
        """
        doc_type = crawlers_category['newzfwj']
        spider_name = crawlers_name['newzfwj']
        await self.newzfwj_spider.collector(url=doc_type, spider_name=spider_name)

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
                    _editor = ''.join(row.xpath('./div[@class="lie3"]//text()')).strip()
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

    async def parse_detail_page(self, html_text: str):
        """
        parse detail page|
        :param html_text:
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

        texts = html.xpath('//div[@class="artleft"]//text()')
        cleaned_texts = [clean_text(text) for text in texts]
        file_status = ''.join(html.xpath('//span[@id="invalidTime"]/text()')).strip()

        editor = ''.join(html.xpath('//span[@class="n_wh"]/text()')).strip()

        all_related_links = self.extract_related_links(html, '//div[@id="xqygb22"]//li//a', 'https://www.sc.gov.cn')
        all_appendix = self.extract_related_links(html, xpath_query, f'{extract_url_base(self.page.url)}/')
        all_appendix = list(set(all_appendix))
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

    async def run(self):
        """
        run crawlers
        :return:
        """
        self.logger.info('start running crawlers...')
        await self.get_gfxwj()
        # await self.get_newzfwj()


def extract_url_base(url):
    parts = url.split('/')
    for i in range(len(parts)):
        if len(parts[i]) == 4 and parts[i].isdigit() and i + 3 < len(parts):
            if parts[i + 1].isdigit() and parts[i + 2].isdigit():
                return '/'.join(parts[:i + 3])
    return ''
