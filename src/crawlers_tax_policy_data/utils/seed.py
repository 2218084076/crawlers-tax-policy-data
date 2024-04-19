"""load seed"""
import logging
from datetime import datetime

from crawlers_tax_policy_data.repositories.redis import RedisAsyncio


class Seed:
    def __init__(self):
        now = datetime.now()
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.redis = RedisAsyncio()

    async def load_seed(self, name: str, content: str):
        """
        Load the specified city, and all article links in the list page are the details pages to be collected.

        载入指定城市，列表页中所有文章链接，即为待采集的详情页
        :param name:
        :param content:
        :return:
        """
        self.logger.debug('Load seed name: %s ,content: %s', name, content)
        await self.redis.add_set(
            name=name,
            value=content
        )
