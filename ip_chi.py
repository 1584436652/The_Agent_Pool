from random import choice

from pymongo import MongoClient


class MongodbIP:
    """
    代理ip
    """

    def __init__(self):
        # mongodb数据库操作对象
        self.client = MongoClient(host='127.0.0.1', port=27017)
        # 数据插⼊的数据库与集合
        self.coll = self.client["IP"]["IPAddressPool"]
        self.__ip_library = []

    @property
    def ip_library(self):
        for ip in self.coll.find({}, {'_id': 0}):
            self.__ip_library.append(ip)
        return self.__ip_library

    def ip(self):
        use_ip = choice(self.ip_library)
        print("当前使用ip：{}".format(use_ip))
        return use_ip


if __name__ == '__main__':
    mo = MongodbIP()
    to = 10
    while to > 1:
        mo.ip()
        to -= 1
