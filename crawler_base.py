import requests
from pymongo import MongoClient
from retry import retry
from ip_chi import MongodbIP

from Ua import ua


class CrawlerBase(object):

    def __init__(self):
        self.headers = {
            'User-Agent': ua(),
            'Referer': 'https://www.zdaye.com/free/2/?https=1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,'
                      'image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
        }
        self.proxies = {'https': 'https://58.47.159.147:8001'}
        # mongodb数据库操作对象
        self.client = MongoClient(host='127.0.0.1', port=27017)
        # 数据插⼊的数据库与集合
        self.coll = self.client["IP"]["IPAddressPool"]

    @retry(tries=2, delay=3)
    def make_response(self, url, method=None, timeout=None, **kwargs):
        _method = "GET" if not method else method
        _maxTimeout = timeout if timeout else 3
        print(f'正在请求-----')
        try:
            response = requests.request(method=_method, url=url, timeout=_maxTimeout, **kwargs)
            response.keep_alive = False
            print(response.status_code)
            assert response.status_code == 200
            return response
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ProxyError, requests.exceptions.SSLError) as e:
            print(e)

    def parse(self, res):
        pass

    @staticmethod
    def ip_verify(proxies):
        """
        检验代理ip是否可用
        :param proxies: 代理  example->{ 'https': 'https://58.47.159.147:8001'}
        :return:
        """
        print(f"我在ip_verify检验：{proxies}")
        verify_url = "https://httpbin.org/ip"
        headers = {'User-Agent': ua()}
        try:
            verify_req = requests.get(verify_url, headers=headers, proxies=proxies, timeout=3)
            if verify_req.json()["origin"]:
                print(f"{verify_req.json()['origin']},代理有效！！！")
                return proxies
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ProxyError, requests.exceptions.SSLError):
            print(f"{proxies}请求超时，代理无效！！！")
            return None

    def ip_save_to_mongodb(self, items):
        """
        网站爬取的代理IP存储MongoDB
        :param items:
        :return:
        """
        # self.coll.insert_one(items)
        self.coll.update_one({"https": items["https"]}, {'$set': {"https": items["https"]}}, True)

    def run(self, url, method, judge=True, **kwargs):
        res = self.make_response(url=url, method=method, **kwargs)
        result = res.text if judge else res.json()
        return self.parse(result)


if __name__ == '__main__':
    #  'https': 'https://58.47.159.147:8001'
    proxy_ip = [
        {'https': 'https://113.214.48.5:8000'},
        {'https': 'https://58.47.159.147:8001'},
        {'https': 'https://113.238.142.208:3128'},
        {'https': 'https://120.52.73.105:18080'},
        {'https': 'https://223.100.215.25:8080'},
        # {'https': 'https://58.209.234.8:3389'},
        {'https': 'https://117.161.75.82:3128'}
    ]
    p = {'https': 'https://121.43.190.89:3128'}
    de = CrawlerBase()
    pa = 3
    while pa > 0:
        dats = de.ip_verify(p)
        print(dats)
        if dats:
            de.ip_save_to_mongodb(dats)
        pa -= 1
