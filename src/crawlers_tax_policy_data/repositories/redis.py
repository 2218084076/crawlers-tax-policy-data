"""Redis Repository"""

import aioredis

from crawlers_tax_policy_data.config import settings


class RedisAsyncio:
    """RedisAsyncio"""
    client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    async def get_hash(self, name: str, key: str):
        """
        get hash from redis
        :param name:
        :param key:
        :return:
        """
        res = await self.client.hget(name=name, key=key)
        return res

    async def write_hash(self, name: str, key: str, value: str):
        """
        write hash to redis
        :param name:
        :param key:
        :param value:
        :return:
        """
        await self.client.hset(name=name, key=key, value=value)

    async def add_set(self, name: str, value: str):
        """
        add set
        :param name:
        :param value:
        :return:
        """
        await self.client.sadd(name, value)

    async def pop_set(self, name: str, index: int = 1):
        """
        pop a set
        :param index:
        :param name:
        :return:
        """
        res = await self.client.spop(name, index)
        return res

    async def check_table(self, name: str):
        """
        check if table exists
        :param name:
        :return:
        """
        keys = await self.client.keys()
        if name in keys:
            return False
        return True

    async def sscan_set(self, name: str):
        """
        获取 set 所有元素
        :param name:
        :return:
        """
        cursor = b'0'
        results = []
        while cursor:
            cursor, values = await self.client.sscan(name, cursor=cursor, count=100)
            results.extend(values)
        return results
