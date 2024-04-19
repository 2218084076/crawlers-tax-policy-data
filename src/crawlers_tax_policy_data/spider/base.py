import logging
import time

import undetected_chromedriver as uc


class BaseSpider:
    def __init__(self):
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

    @staticmethod
    def queue_name():
        raise NotImplementedError()

    @property
    def headers(self):
        return {}

    def get_cookie(self, url: str):
        """
        get cookie
        :param url:
        :return:
        """
        self.logger.info('get cookie: %s' % url)
        driver = uc.Chrome()

        driver.get(url)
        time.sleep(3)
        cookies = driver.get_cookies()
        new_cookies = ''
        for cookie in cookies:
            name = cookie['name']
            value = cookie['value']

            items = f'{name}={value};'
            new_cookies += items

        print(new_cookies)

        self.headers['Cookie'] = new_cookies
        driver.close()
