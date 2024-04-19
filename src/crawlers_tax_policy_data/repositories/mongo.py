"""Mongo Repository"""
import logging

import pandas as pd
from pymongo import MongoClient
from pymongo.collection import Collection

from crawlers_tax_policy_data.config import settings


class MongoRepository:
    """Mongo Repository"""

    def __init__(self, collection_name: str):
        self.index_dic = {'Code': '$Code',
                          'CodeDesc': '$CodeDesc',
                          'CountryCode': '$CountryCode',
                          'Country': '$Country',
                          'CustomsCode': '$CustomsCode',
                          'CustomsRegime': '$CustomsRegime',
                          'ProvinceCode': '$ProvinceCode',
                          'Province': '$Province',
                          'Qty1': '$Qty1',
                          'Qty1Unit': '$Qty1Unit',
                          'Qty2': '$Qty2',
                          'Qty2Unit': '$Qty2Unit',
                          'ValueUSD': '$ValueUSD',
                          'Year': '$Year',
                          'Month': '$Month',
                          'ImportOrExport': '$ImportOrExport',
                          }
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.collection_name = collection_name
        self.mongo_client = MongoClient(settings.MONGODB_URL)
        self.db_name = settings.MONGODB_NAME

    @property
    def collection(self) -> Collection:
        """
        collection
        :return:
        """
        collection = self.mongo_client.get_database(
            self.db_name).get_collection(self.collection_name)
        return collection

    def write(self, content: dict):
        """
        write
        :param content:
        :return:
        """

        self.collection.insert_one(content)

    def read(self):
        """
        read
        :return:
        """
        data = self.collection.find()
        return data

    def only_write(self, message: dict):
        """
        only write
        唯一写入 用来写入爬虫状态
        :param message:
        :return:
        """
        date_dic = {key: value for key, value in message.items() if key in {'Export'}}
        quantity = self.collection.count_documents(date_dic)
        if quantity == 1:
            self.collection.update_one(self.collection.find_one(), {'$set': message})
            self.logger.debug('Update crawler status %s', message)
        if quantity == 0:
            self.collection.insert_one(message)
            self.logger.debug('Create crawler state %s', message)

    def check(self, key: dict):
        """
        check
        :return:
        """
        return self.collection.find_one(key)

    def delete(self):
        """
        delete
        :return:
        """
        self.collection.drop()

    def get(self, key: dict):
        """
        get
        通过条件筛选
        :param key:
        :return:
        """
        return self.collection.find(key)

    def total(self, conditions: dict):
        """total"""
        data = self.get(conditions)
        df = pd.DataFrame(list(data))
        return df.shape[0]

    def remove_duplicates(self):
        """
        remove_duplicates
        去重
        :return:
        """
        self.logger.debug('Remove duplicates !')
        redundant_data = self.collection.aggregate(
            [
                {'$group': {'_id': self.index_dic, 'uniqueIds': {'$addToSet': "$_id"}, 'count': {'$sum': 1}}},
                {'$match': {'count': {'$gt': 1}}}
            ], allowDiskUse=True)

        for datas in redundant_data:
            first = True
            self.logger.debug('Redundant data %s', datas)
            for data in datas['uniqueIds']:
                if first:
                    first = False
                else:
                    self.collection.delete_one({'_id': data})