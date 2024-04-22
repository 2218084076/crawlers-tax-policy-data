# encoding:utf-8
import time
from pathlib import Path

from lxml import etree

from crawlers_tax_policy_data.config import settings
from crawlers_tax_policy_data.spider.base import BaseSpider
from crawlers_tax_policy_data.storage.local import save_data
from crawlers_tax_policy_data.utils.utils import date_obj


class GovSpider(BaseSpider):
    """
    gov spider
    """

    @property
    def url(self):
        """
        url
        :return:
        """
        return 'https://www.gov.cn/zhengce/xxgk/'

    @property
    def headers(self):
        """
        headers
        :return:
        """
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd", "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "max-age=0", "Connection": "keep-alive",
            "Cookie": "wdcid=152a07eba35f5508; SERVERID=adb2d3a906b8c5e3f02ddd9c20949df0|1713672860|1713672860; wdlast=1713717051; wdses=7be7c258faa948c1",
            "Host": "www.gov.cn", "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin", "Sec-Fetch-User": "?1", "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"",
            "sec-ch-ua-mobile": "?0"
        }

    @property
    def payload(self):
        return {"code": "18122f54c5c", "thirdPartyCode": "thirdparty_code_107", "thirdPartyTableId": 30,
                "resultFields": ["pub_url", "maintitle", "fwzh", "cwrq", "publish_time"], "trackTotalHits": "true",
                "searchFields": [{"fieldName": "maintitle", "searchWord": ""}], "isPreciseSearch": 0,
                "sorts": [{"sortField": "publish_time", "sortOrder": "DESC"}],
                "childrenInfoIds": [[1108, 1107, 1106, 1105, 1104, 1103, 1102, 7547, 7548, 7549, 1101, "1100"]],
                "pageSize": 20, "pageNo": 1}

    def get_news(self):
        """
        post request the data

        Parse according to the specified date
        cookies are valid for 30 minutes
        :return:
        """
        check_date = settings.CRAWLERS_DATE
        check_date_obj = date_obj(check_date)
        self.sync_init_page()
        self.page.goto(self.url)
        check_date = f'{check_date_obj.year}年{int(check_date_obj.month):02d}月{int(check_date_obj.day):02d}日'
        time.sleep(0.5)
        self.logger.info('post %s,%s', self.url, self.page)
        # All details page links to be crawled
        detail_pages = self.parse_list(
            check_date=check_date
        )

        self.page.close()
        self.browser.close()

        for _page in detail_pages:
            repo = self.get_req(
                url=_page.get('link'),
                headers=self.headers,
            )
            repo.encoding = 'utf-8'  # fix garbled characters in requests
            self.logger.info('get %s', _page)
            detail_data = self.parse_detail_page(repo.text)
            current_news_data = {}
            current_news_data.update({
                'link': _page.get("link"),
                'title': detail_data['info'][detail_data['info'].index('标\u3000\u3000题：') + 1],
                'editor': detail_data['info'][detail_data['info'].index('发文字号：') + 1],
                'date': detail_data['info'][detail_data['info'].index('发布日期：') + 1],
                'text': detail_data.get('text').replace('\u3000', ' '),
                'related_documents': detail_data.get('related_documents'),
                'appendix': ''
            })
            self.logger.debug(current_news_data)
            save_data(
                content=current_news_data,
                file_path=Path(
                    settings.GOV_OUTPUT_PAHT) / 'www.gov.cn-zhengce-xxgk' / f'{check_date}-public-information.csv'
            )

    def parse_list(self, check_date: str) -> list:
        """
        parse list page
        :param check_date:
        :return:
        """
        res = []

        def parse_news_items(items):
            """ Helper function to parse news items """
            for item in items:
                _page_date = item.locator('td').nth(-1).text_content()
                self.page.wait_for_timeout(500)
                if _page_date == check_date:
                    _title = item.locator('a').text_content()
                    _link = item.locator('a').get_attribute('href')
                    res.append({'title': _title, 'link': _link})
                    self.logger.info(f'Added news item: {_title}')

        # Initial parse of news items
        all_news = self.page.locator('//tbody[@id="xxgkzn_list_tbody_ID"]//tr').all()
        self.logger.info('Parsing text contents for the first page')
        parse_news_items(all_news)

        # Check if pagination is needed and execute
        if all_news and all_news[-1].locator('td').nth(-1).text_content() == check_date:
            self.page.locator('//*[@id="newPage"]/div[1]/div[8]').click()
            self.page.wait_for_timeout(500)  # Simulating waiting for page to load
            all_news = self.page.locator('//tbody[@id="xxgkzn_list_tbody_ID"]//tr').all()
            self.logger.info('Parsing text contents for the next page')
            parse_news_items(all_news)

        return res

    def parse_detail_page(self, html_text: str):
        """
        parse detail page

        :param html_text:
        :return:
        """
        res = {}
        self.logger.info('parse detail_page text data')
        html = etree.HTML(html_text, etree.HTMLParser(encoding="utf-8"))  # fix garbled characters in requests
        tr_list = html.xpath('//tbody')[1].findall('tr')
        data = []
        for tr in tr_list:
            for d in tr.findall('td'):
                if d.text is not None:
                    data.append(d.text)
                else:
                    data.append(''.join(d.xpath('b/text()')))
        # 正文
        text = [
            p.text if p.text is not None else ' '.join(p.xpath('strong/text()'))
            for p in html.xpath('//div[@class="trs_editor_view TRS_UEDITOR trs_paper_default trs_web"]')[0].findall('p')
        ]
        # 相关链接
        related_documents_li = html.xpath('//ul[@class="jiedu_list bt13"]//li')
        related_documents = []
        for li in related_documents_li:
            _title = ''.join(li.xpath('a/text()'))
            _link = ''.join(li.xpath('a/@href'))
            related_documents.append(f'{_title} {_link}')

        res.update({
            'text': ''.join(text),
            'info': data,
            'related_documents': ','.join(related_documents),
            'appendix': ''
        })

        return res

    def run(self):
        """
        run crawlers
        :return:
        """
        self.get_news()
