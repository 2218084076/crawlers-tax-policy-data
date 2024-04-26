"""
北京市人民政府
https://www.beijing.gov.cn/zhengce/zhengcefagui/
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


def extract_url_base(url: str):
    parts = url.split('/')
    for i in range(len(parts)):
        if len(parts[i]) == 6 and parts[i].isdigit():
            return '/'.join(parts[:i + 1])
    return None


class BjGovSpider(BaseSpider):
    """
    北京市人民政府 爬虫
    """
    folder = 'beijing.gov.cn'

    def __init__(self):
        super().__init__()
        self.status_xpath = '//li[@class="yxx"]//span//text()'
        self.title_xpath = '//div[@class="header"]//p/text()'

    @property
    def url(self):
        """
        北京市人民政府 政策文件 链地址
        :return:
        """
        return 'https://www.beijing.gov.cn/zhengce/zhengcefagui/'

    @property
    def headers(self):
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": "Path=/; __jsluid_s=b3c15f33d5fb27be6570bb47228bb549; _va_ses=*; JSESSIONID=M2RkNDU3YTQtZWQ1Yi00YjY5LWFiY2UtOTc2ZGYwMjlmMDkw; arialoadData=false; _va_id=db017d68f37f750d.1714012327.1.1714012478.1714012327.",
            "Host": "www.beijing.gov.cn",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
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

    async def get_public_info(self):
        """
        get public information
        :return:
        """
        start_date, end_date = self.check_date
        self.logger.info('Start collecting 北京市人民政府 政策文件 %s %s-%s data', self.url, start_date, end_date)
        repo = await self.async_get_req(
            url=self.url,
            headers=self.headers
        )
        repo.encoding = 'utf-8'
        self.logger.info('%s %s', self.url, repo)

        detail_pages = await self.parse_news_list(html_text=repo.text, start_date=start_date, end_date=end_date)

        if not detail_pages:
            self.logger.warning('北京市人民政府 政策文件  %s-%s no data', start_date, end_date)
            return ''

        for _p in detail_pages:
            _link = _p.get('link')
            if 'pdf' in _link:
                save_data(
                    content={'link': _link, 'date': _p['date'], 'title': _p['title']},
                    file_path=Path(
                        settings.GOV_OUTPUT_PAHT) / self.folder / f'{start_date}-{end_date}' / f'{start_date}-{end_date}-public'
                                                                                               f'-information.csv'
                )
            else:
                detail_repo = await self.async_get_req(
                    url=_link,
                    headers=self.headers
                )
                detail_repo.encoding = 'utf-8'
                _html_text = detail_repo.text

                detail_data = await self.parse_detail_page(html_text=_html_text, prefix=extract_url_base(_link))

                _title = re.sub(r'\s+', '', detail_data["title"])
                detail_page_html_file = Path(
                    settings.GOV_OUTPUT_PAHT
                ) / self.folder / f'{start_date}-{end_date}' / f'''{_p['date']}-{_title}.html'''
                self.save_html(
                    html_content=_html_text,
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
                        settings.GOV_OUTPUT_PAHT) / self.folder / f'{start_date}-{end_date}' / f'{start_date}-{end_date}-public'
                                                                                               f'-information.csv')

                await asyncio.sleep(0.3)
        self.logger.info('北京市人民政府 政策文件  %s-%s Data collection completed', start_date, end_date)

    async def parse_news_list(
            self,
            html_text: str,
            start_date: str,
            end_date: str
    ):
        """
        parse news list
        :param html_text:
        :param start_date:
        :param end_date:
        :return:
        """
        self.logger.info('parse Beijing policy document list page')
        res = []
        html = etree.HTML(html_text, etree.HTMLParser(encoding="utf-8"))

        def parse_news_items(all_row: list):
            """
            parse news items
            :param all_row:
            :return:
            """
            for row in all_row:
                _page_date = clean_text(''.join(row.xpath('./span/text()')))
                _date = datetime.strptime(
                    _page_date,
                    '%Y-%m-%d'
                ).date()
                if (datetime.strptime(start_date, '%Y-%m-%d').date()
                        <= _date
                        <= datetime.strptime(end_date, '%Y-%m-%d').date()):
                    _title = clean_text(''.join(row.xpath('./a/text()')))
                    _link = clean_text(
                        "".join(row.xpath("./a/@href"))
                    ).replace('./', 'https://www.beijing.gov.cn/zhengce/zhengcefagui/')
                    res.append({'title': _title, 'link': _link, 'date': _page_date, })

        li_list = html.xpath('//ul[@class="default_news"]//li')
        parse_news_items(li_list)

        return res

    async def parse_detail_page(self, html_text: str, prefix: str):
        """
        parse detail page
        :param prefix:
        :param html_text:
        :return:
        """
        res = {}

        file_xpath = self.build_file_xpath()
        xpath_query = f'//a[{file_xpath}]'

        html = etree.HTML(
            html_text,
            etree.HTMLParser(encoding="utf-8")  # fix garbled characters in requests
        )
        file_status = self.extract_file_status(html)
        title = self.extract_title(html)
        texts = html.xpath('//div[@class="leftbox clearfix"]//p//text()')
        cleaned_texts = [clean_text(text) for text in texts]

        editor = ''.join(html.xpath('//li[@class="fwzh"]//span/text()')).strip()
        editor = re.sub(r'[\u200b\u2004\u2002\u2003\xa0\u3000]+', lambda m: '' * len(m.group()), editor)
        if editor == "〔〕号":
            editor = "----"
        all_related_links = self.extract_links(html, '//div[@class="relevantdoc xgjd"]/ul//a')

        all_appendix = list(set(extract_links(html, xpath_query, prefix)))

        res.update({
            'title': title,
            'text': '\n'.join(cleaned_texts).strip(),
            'related_documents': ',\n'.join(all_related_links),
            'state': ''.join(file_status),
            'appendix': ',\n'.join(all_appendix).replace('\xa0', ''),
            'editor': editor
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

    def extract_file_status(self, html):
        """
        Extract bulletin status
        :param html:
        :return:
        """
        status_text = clean_text(''.join(html.xpath(self.status_xpath)))
        if status_text == '是':
            return '现行有效'
        return '失效'

    async def run(self):
        """
        run crawlers
        :return:
        """
        self.logger.info('start running crawlers...')
        await self.get_public_info()


def extract_links(html, xpath, prefix: str):
    """
    Extract the links according to the given XPath
    :param prefix:
    :param html:
    :param xpath:
    :return:
    """
    return [''.join(link.xpath('./text()')) + ' ' + ''.join(link.xpath('@href')).replace('./', f'{prefix}/') for
            link in
            html.xpath(xpath)]
