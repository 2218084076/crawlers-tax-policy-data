# encoding:utf-8
"""
https://www.sz.gov.cn/cn/xxgk/zfxxgj/tzgg/index.html
"""
import logging

import requests
from lxml import etree
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

disable_warnings(InsecureRequestWarning)


class SZGovSpider:

    def __init__(self):
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.sz_gov_url = 'https://www.sz.gov.cn/cn/xxgk/zfxxgj/tzgg/'
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/124.0.0.0 Safari/537.36'
        }

    def get_list(self, start_date: str, end_date: str):
        """
        get list
        :param start_date:
        :param end_date:
        :return:
        """
        respo = requests.get(url=self.sz_gov_url, headers=self.headers, verify=False)
        self.logger.info('get list sz_gov %s', respo.status_code)
        res = self.parse(respo.text, start_date, end_date)

    def parse(self, html_text: str, start_date: str, end_date: str):
        """
        parse html text
        :param start_date:
        :param end_date:
        :param html_text:
        :return:
        """
        self.logger.info('parse html')
        html = etree.HTML(html_text)
        print(html)
        return ''
