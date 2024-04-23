from datetime import datetime
from pathlib import Path

from lxml import etree

from crawlers_tax_policy_data.config import settings
from crawlers_tax_policy_data.spider.base import BaseSpider
from crawlers_tax_policy_data.storage.local import save_data


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

    async def get_news(self):
        """
        post request the data

        Parse according to the specified date
        cookies are valid for 30 minutes
        :return:
        """
        check_date = self.date
        if isinstance(check_date, dict):
            start_date = f'{check_date["start"].year}年{int(check_date["start"].month):02d}月{int(check_date["start"].day):02d}日'
            end_date = f'{check_date["end"].year}年{int(check_date["end"].month):02d}月{int(check_date["end"].day):02d}日'
        else:
            start_date = f'{check_date.year}年{int(check_date.month):02d}月{int(check_date.day):02d}日'
            end_date = f'{check_date.year}年{int(check_date.month):02d}月{int(check_date.day):02d}日'

        await self.init_page()
        await self.page.goto(self.url)
        await self.page.wait_for_timeout(400)
        self.logger.info('post %s', self.page)
        # All details page links to be crawled
        detail_pages = await self.parse_list(
            start_date=start_date,
            end_date=end_date
        )
        await self.stop_page()
        if not detail_pages:
            self.logger.info('<%s> no data', check_date)
            return []

        for _page in detail_pages:
            repo = await self.async_get_req(
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
            save_data(
                content=current_news_data,
                file_path=Path(
                    settings.GOV_OUTPUT_PAHT) / 'www.gov.cn-zhengce-xxgk' / f'{start_date}-{end_date}-public'
                                                                            f'-information.csv'
            )
        self.logger.debug('Details page content parsing complete %s', self.url)

    async def parse_list(self, start_date: str, end_date: str) -> list:
        """
        parse list page
        :param start_date: Start date in 'YYYY年MM月DD日' format
        :param end_date: End date in 'YYYY年MM月DD日' format
        :return:
        """
        res = []

        async def parse_news_items(items):
            """ Helper function to parse news items """
            for item in items:
                _page_date_str = await item.locator('td').nth(-1).text_content()
                _page_date = datetime.strptime(
                    _page_date_str,
                    '%Y年%m月%d日'
                ).date()
                await self.page.wait_for_timeout(400)
                if (datetime.strptime(start_date, '%Y年%m月%d日').date()
                        <= _page_date
                        <= datetime.strptime(end_date, '%Y年%m月%d日').date()
                ):
                    _title = await item.locator('a').text_content()
                    _link = await item.locator('a').get_attribute('href')
                    res.append({'title': _title, 'link': _link})
                    self.logger.debug(f'Added news item: {_title} on {_page_date_str}')

        # Initial parse of news items
        all_news = await self.page.locator('//tbody[@id="xxgkzn_list_tbody_ID"]//tr').all()
        self.logger.info('Parsing text contents for the first page')
        await parse_news_items(all_news)

        # Implementing pagination if needed, check the last news date if pagination is required
        last_news_date_str = await all_news[-1].locator('td').nth(-1).text_content()
        last_news_date = datetime.strptime(last_news_date_str, '%Y年%m月%d日').date()

        while last_news_date >= datetime.strptime(start_date, '%Y年%m月%d日').date():
            # Check if pagination is needed based on the date of the last news item
            await self.page.locator('//*[@id="newPage"]/div[1]/div[8]').click()
            self.logger.info('Check next page, Get more %s', self.page)
            await self.page.wait_for_timeout(400)
            all_news = await self.page.locator('//tbody[@id="xxgkzn_list_tbody_ID"]//tr').all()
            self.logger.info('Parsing text contents for the next page')
            await parse_news_items(all_news)
            last_news_date_str = await all_news[-1].locator('td').nth(-1).text_content()
            last_news_date = datetime.strptime(last_news_date_str, '%Y年%m月%d日').date()

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

    async def run(self):
        """
        run crawlers
        :return:
        """
        await self.get_news()
