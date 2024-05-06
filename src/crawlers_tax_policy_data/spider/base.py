"""
Base class for crawlers
@author: Terry
"""
import logging
import pathlib
import re
from datetime import datetime

import httpx
import playwright
import requests
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright

from crawlers_tax_policy_data.config import settings
from crawlers_tax_policy_data.utils.utils import date_obj


class BaseSpider:
    """
    Base class for crawlers
    """

    def __init__(self):
        self.now_date = None
        self.browser: playwright.sync_api._generated.Browser | playwright.async_api._generated.Browser | None = None
        self.page: playwright.sync_api._generated.Page | playwright.async_api._generated.Page | None = None
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.file_types = ['.pdf', '.xls', '.xlsx', '.doc', '.docx', '.ppt', '.pptx', '.txt', '.odt', '.wps']
        self.pattern = r'^\S+〔\d+〕\d+号$'

    @property
    def date(self):
        """
        Determine the crawler crawl date

        If the data start date and end date are specified in the configuration,
        the dates in the configuration will be used.

        If not specified, the current date is calculated as the page data date
        :return:
        """
        self.now_date = datetime.now()
        crawlers_start_date = settings.START_DATE
        crawlers_end_date = settings.END_DATE

        if crawlers_start_date:
            start_date = date_obj(crawlers_start_date)
        else:
            start_date = self.now_date

        if crawlers_end_date:
            end_date = date_obj(crawlers_end_date)
        else:
            end_date = start_date

        if start_date == end_date:
            return start_date
        else:
            return {'start': start_date, 'end': end_date}

    @property
    def headers(self):
        """
        headers
        :return:
        """
        return {}

    @property
    def url(self):
        """
        url
        :return:
        """
        return ''

    def get_req(self, url: str, **kwargs):
        """
        get requests
        :param url:
        :return:
        """
        self.logger.info('use sync request get %s', url)
        return requests.get(url=url, **kwargs, timeout=120)

    async def post_req(self, url: str, **kwargs):
        """
        post requests
        :param url:
        :param kwargs:
        :return:
        """
        self.logger.info('use async request post %s', url)
        async with httpx.AsyncClient() as client:
            repo = await client.post(url=url, **kwargs)
        return repo

    def get_cookies(self, url: str):
        """
        get cookies
        :param url:
        :return:
        """
        self.sync_init_page()
        self.page.goto(url)
        cookies = self.page.context.cookies()
        self.page.close()
        self.browser.close()
        cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}
        return cookies_dict

    async def async_get_req(self, url: str, **kwargs) -> httpx.Response:
        """
        async get requests
        :param url:
        :param kwargs:
        :return:
        """
        self.logger.info('use async request get %s', url)
        async with httpx.AsyncClient() as client:
            repo = await client.get(url=url, **kwargs)
        return repo

    def sync_init_page(self):
        """
        sync get by playwright
        :return:
        """
        p = sync_playwright().start()
        self.browser = p.webkit.launch(headless=settings.HEADLESS)
        self.page = self.browser.new_page()

    async def init_page(self):
        """
        async get by playwright
        :return:
        """
        p = await async_playwright().start()
        self.browser = await p.webkit.launch(headless=settings.HEADLESS)
        self.page = await self.browser.new_page()

    async def stop_page(self):
        """
        stop page
        :return:
        """
        await self.page.close()
        await self.browser.close()

    @property
    def check_date(self):
        """
        check date
        :return:
        """
        raise NotImplementedError()

    def build_file_xpath(self):
        """
        Generate an XPath query string based on a list of file types
        :return:
        """
        return " or ".join(
            [f"substring(@href, string-length(@href) - string-length('{ft}') + 1) = '{ft}'" for ft in self.file_types]
        )

    @staticmethod
    def extract_links(html, xpath):
        """
        Extract the links according to the given XPath
        :param html:
        :param xpath:
        :return:
        """
        return [''.join(link.xpath('.//text()')) + ' ' + ''.join(link.xpath('@href')) for link in html.xpath(xpath)]

    def is_match(self, text):
        """
        Check whether the text matches the pattern
        :param text:
        :return:
        """
        original_text = text.replace(" ", "")

        formatted_text = re.sub(r"(\d+)年第(\d+)号", r"〔\1〕\2号", original_text)

        if not text:
            return False
        if '其他文件' in text:
            return 1
        return bool(re.match(self.pattern, formatted_text))

    def save_html(self, html_content: str, file: pathlib.Path):
        """
        save html content
        :param html_content:
        :param file:
        :return:
        """
        file.parent.mkdir(parents=True, exist_ok=True)
        self.logger.info('Save html content to %s', file)
        with open(file, 'w', encoding='utf-8') as f:
            f.write(html_content)
