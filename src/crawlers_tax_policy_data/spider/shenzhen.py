# encoding:utf-8
"""
shenzhen gov crawlers
https://www.sz.gov.cn/cn/xxgk/zfxxgj/zcfg/szsfg/index.html
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


class ShenZhengSpider(BaseSpider):
    """
    shenzhen gov crawlers
    """
    folder = 'sz.gov.cn'

    @property
    def url(self):
        """
        url
        :return:
        """
        return 'https://www.sz.gov.cn/cn/xxgk/zfxxgj/zcfg/szsfg/index.html'

    @property
    def headers(self):
        """
        headers
        :return:
        """
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                      "*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": "Path=/; _trs_uv=lv6ea1op_850_3lfc; Path=/; _trs_ua_s_1=lvakroia_850_1ora; arialoadData=false",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/124.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Chromium\";v=\"124\", \"Google Chrome\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }

    @property
    def payload(self):
        return {}

    async def get_news(self):
        """
        get news
        :return:
        """
        check_date = self.date
        if isinstance(check_date, dict):
            start_date = f'{check_date["start"].year}年{int(check_date["start"].month):02d}月{int(check_date["start"].day):02d}日'
            end_date = f'{check_date["end"].year}年{int(check_date["end"].month):02d}月{int(check_date["end"].day):02d}日'
        else:
            start_date = f'{check_date.year}年{int(check_date.month):02d}月{int(check_date.day):02d}日'
            end_date = f'{check_date.year}年{int(check_date.month):02d}月{int(check_date.day):02d}日'
        self.logger.info('Start collecting %s %s-%s data',
                         '深圳市人民政府 https://www.sz.gov.cn/cn/xxgk/zfxxgj/zcfg/szsfg/index.html',
                         start_date, end_date)
        await self.init_page()
        await self.page.goto(self.url)
        await self.page.wait_for_timeout(400)
        html_text = await self.page.content()

        list_page_data = await self.parse_news_list(
            html_text=html_text,
            start_date=start_date,
            end_date=end_date
        )

        if not list_page_data:
            self.logger.warning('<%s> no data', check_date)
            return ''

        self.logger.info('%s article has been updated', len(list_page_data))
        for _p in list_page_data:
            # repo.encoding = 'utf-8'
            _link = _p.get('link')
            await self.page.goto(_link)
            page_content = await self.page.content()
            detail_data = self.parse_detail_page(page_content)

            # save html file
            _title = re.sub(r'\s+', '', detail_data["title"])
            detail_page_html_file = Path(
                settings.GOV_OUTPUT_PAHT
            ) / self.folder / f'{start_date}-{end_date}' / f'''{detail_data["date"]}-{_title}.html'''
            self.save_html(
                html_content=page_content,
                file=detail_page_html_file
            )

            detail_data.update({'link': _link, 'html_file': str(detail_page_html_file)})

            save_data(
                content=detail_data,
                file_path=Path(
                    settings.GOV_OUTPUT_PAHT) / self.folder / f'{start_date}-{end_date}' / f'{start_date}-{end_date}-public-information.csv'
            )
            await asyncio.sleep(0.3)

        self.logger.debug('Details page content parsing complete %s', self.folder)
        await self.stop_page()

    async def parse_news_list(self, html_text: str, start_date: str, end_date: str):
        res = []
        self.logger.info('parse news list pages')

        def parse_news_items(all_li):
            """
            parser news items
            :param all_li:
            :return:
            """
            for li in all_li:
                _date = li.xpath('./span[2]/text()')[0]
                _page_date = datetime.strptime(
                    _date,
                    '%Y年%m月%d日'
                ).date()
                if (datetime.strptime(start_date, '%Y年%m月%d日').date()
                        <= _page_date
                        <= datetime.strptime(end_date, '%Y年%m月%d日').date()
                ):
                    _title = li.xpath('./div[@class="list_name"]/a/text()')[0]
                    _link = li.xpath('./div[@class="list_name"]/a/@href')[0]
                    res.append({'title': _title, 'link': _link})

        html = etree.HTML(html_text, etree.HTMLParser(encoding="utf-8"))
        li_list = html.xpath('//div[@class="zx_ml_list"]//li')[1:]
        parse_news_items(li_list)

        last_news_date_str = li_list[-1].xpath('./span[2]/text()')[0]
        last_news_date = datetime.strptime(last_news_date_str, '%Y年%m月%d日').date()
        while last_news_date >= datetime.strptime(start_date, '%Y年%m月%d日').date():
            await self.page.locator('//a[@class="next"]').click()
            self.logger.info('Check next page, Get more %s', self.page)
            await self.page.wait_for_timeout(400)
            next_html_text = await self.page.content()
            next_html = etree.HTML(next_html_text, etree.HTMLParser(encoding="utf-8"))
            next_li_list = next_html.xpath('//div[@class="zx_ml_list"]//li')[1:]
            parse_news_items(next_li_list)

            last_news_date_str = next_li_list[-1].xpath('./span[2]/text()')[0]
            last_news_date = datetime.strptime(last_news_date_str, '%Y年%m月%d日').date()

        return res

    def parse_detail_page(self, html_text: str):
        """
        parse detail page
        :param html_text:
        :return:
        """
        res = {}
        html = etree.HTML(html_text, etree.HTMLParser(encoding="utf-8"))  # fix garbled characters in requests
        title = re.sub(r'\s+', '', clean_text(''.join(html.xpath('//div[@class="tit"]/h1/text()'))))
        editor = ''.join(html.xpath('//div[@class="xx_con"][1]/p[6]/text()'))
        date = ''.join(html.xpath('//div[@class="xx_con"][1]/p[4]/text()')).strip()
        related_documents = ',\n'.join(
            [' - '.join((item.text, ''.join(item.xpath('@href')))) for item in html.xpath('//div[@class="fjdown"]//a')]
        )
        file_xpath = self.build_file_xpath()
        xpath_query = f'//a[{file_xpath}]'
        all_appendix = self.extract_links(html, xpath_query)
        texts = html.xpath('//div[@class="news_cont_d_wrap"]//text()')
        cleaned_texts = [clean_text(text) for text in texts]

        res.update({
            'title': title,
            'text': title + '\n'.join(cleaned_texts),
            'editor': editor,
            'date': date,
            'related_documents': related_documents,
            'appendix': ',\n'.join(all_appendix).strip()
        })

        return res

    async def run(self):
        """
        run crawlers
        :return:
        """
        self.logger.info('start running crawlers...')
        await self.get_news()
