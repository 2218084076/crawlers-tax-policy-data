# encoding:utf-8
"""
shenzhen gov crawlers
https://www.sz.gov.cn/cn/xxgk/zfxxgj/zcfg/szsfg/index.html
"""
import re
from pathlib import Path

from lxml import etree

from crawlers_tax_policy_data.config import settings
from crawlers_tax_policy_data.spider.base import BaseSpider
from crawlers_tax_policy_data.storage.local import save_data
from crawlers_tax_policy_data.utils.utils import date_obj


class ShenZhengSpider(BaseSpider):
    """
    shenzhen gov crawlers
    """
    folder = 'www.sz.gov.cn'

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
        check_date = settings.CRAWLERS_DATE
        check_date_obj = date_obj(check_date)
        check_page_date = f'{check_date_obj.year}年{int(check_date_obj.month):02d}月{int(check_date_obj.day):02d}日'
        await self.init_page()
        await self.page.goto(self.url)
        await self.page.wait_for_timeout(400)
        html_text = await self.page.content()
        list_page_data = await self.parse_news_list(html_text, check_page_date)

        if not list_page_data:
            self.logger.warning('%s, No new articles have been updated on the current date', check_page_date)
            return ''

        self.logger.info('%s article has been updated', len(list_page_data))
        for _p in list_page_data:
            # repo.encoding = 'utf-8'
            _link = _p.get('link')
            await self.page.goto(_link)
            page_content = await self.page.content()
            detail_data = self.parse_detail_page(page_content)
            detail_data.update({'link': _link})
            save_data(
                content=detail_data,
                file_path=Path(settings.GOV_OUTPUT_PAHT) / self.folder / f'{check_page_date}-public-information.csv'
            )
        await self.stop_page()

    async def parse_news_list(self, html_text: str, check_date: str):
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
                if _date == check_date:
                    _title = li.xpath('./div[@class="list_name"]/a/text()')[0]
                    _link = li.xpath('./div[@class="list_name"]/a/@href')[0]
                    res.append({'title': _title, 'link': _link})

        html = etree.HTML(html_text, etree.HTMLParser(encoding="utf-8"))
        li_list = html.xpath('//div[@class="zx_ml_list"]//li')[1:]
        parse_news_items(li_list)
        if li_list and li_list[-1].xpath('./span[2]/text()')[0] == check_date:
            await self.page.locator('//a[@class="next"]').click()
            self.logger.debug('Check next page, Get more')
            await self.page.wait_for_timeout(400)
            next_html_text = await self.page.content()
            next_html = etree.HTML(next_html_text, etree.HTMLParser(encoding="utf-8"))
            next_li_list = next_html.xpath('//div[@class="zx_ml_list"]//li')[1:]
            parse_news_items(next_li_list)

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
        title = clean_text(''.join(html.xpath('//div[@class="tit"]/h1/text()')))
        editor = ''.join(html.xpath('//div[@class="xx_con"][1]/p[6]/text()'))
        date = ''.join(html.xpath('//div[@class="xx_con"][1]/p[4]/text()')).strip()
        related_documents = ','.join(
            [' - '.join((item.text, ''.join(item.xpath('@href')))) for item in html.xpath('//div[@class="fjdown"]//a')]
        )
        res.update({
            'title': title,
            'text': title + clean_text(''.join(html.xpath('//div[@class="news_cont_d_wrap"]//text()'))),
            'editor': editor,
            'date': date,
            'related_documents': related_documents,
        })

        return res

    async def run(self):
        """
        run crawlers
        :return:
        """
        self.logger.info('start running crawlers...')
        await self.get_news()


def clean_text(text):
    """
    Used to clean and standardize extracted text
    :param text:
    :return:
    """
    # 使用正则表达式替换空白字符和其他不需要的字符
    text = re.sub(r'[\u3000\n\t]+', ' ', text)
    return text.strip()
