import logging

import httpx
import playwright
import requests
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright

from crawlers_tax_policy_data.config import settings


class TaxSpider:
    def __init__(self):
        self.browser: playwright.sync_api._generated.Browser | playwright.async_api._generated.Browser | None = None
        self.page: playwright.sync_api._generated.Page | playwright.async_api._generated.Page | None = None
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

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

    def get_req(self, url: str, headers: dict):
        """
        get requests
        :param url:
        :param headers:
        :return:
        """
        self.logger.info('use sync request get %s', url)
        return requests.get(url=url, headers=headers)

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
        p = sync_playwright().start()
        self.browser = p.chromium.launch(headless=settings.HEADLESS)
        self.page = self.browser.new_page()

    async def init_page(self):
        """
        async get by playwright
        :return:
        """
        p = await async_playwright().start()
        self.browser = await p.chromium.launch(headless=settings.HEADLESS)
        self.page = await self.browser.new_page()

    async def stop_page(self):
        """
        stop page
        :return:
        """
        await self.page.close()
        await self.browser.close()
