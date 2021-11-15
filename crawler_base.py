import requests
from pymongo import MongoClient
from retry import retry

from Ua import ua


class CrawlerBase(object):

    def __init__(self):
        self.headers = {
            'User-Agent': ua(),

        }
        # mongodb数据库操作对象
        self.client = MongoClient(host='127.0.0.1', port=27017)
        # 数据插⼊的数据库与集合
        self.coll = self.client["IP"]["IPAddressPool"]

    @retry(tries=3, delay=3)
    def make_response(self, method=None, headers=None, timeout=None, **kwargs):
        _method = "GET" if not method else method
        _maxTimeout = timeout if timeout else 3
        print(f'正在请求-----')
        try:
            response = requests.request(method=_method, headers=headers, timeout=_maxTimeout, **kwargs)
            print(response.status_code)
            assert response.status_code == 200
            return response
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ProxyError):
            print("error")

    def parse(self, res):
        pass

    def ip_verify(self, proxies):
        """
        检验代理ip是否可用
        :param proxies: 代理  example->{ 'https': 'https://58.47.159.147:8001'}
        :return:
        """
        print(proxies)
        verify_url = "https://httpbin.org/ip"
        try:
            verify_req = requests.get(verify_url, headers=self.headers, proxies=proxies, timeout=3)
            if verify_req.json()["origin"]:
                print(f"{verify_req.json()['origin']},代理有效！！！")
                return proxies
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ProxyError):
            print(f"{proxies}请求超时，代理无效！！！")

    @staticmethod
    def save_csv(self, text):
        with open('proxies_ip.csv', 'a', encoding='utf-8') as f:
            f.write(text)

    def ip_save_to_mongodb(self):
        pass

    def run(self, method, headers, judge=True, **kwargs):
        res = self.make_response(method=method, headers=headers, **kwargs)
        result = res.text if judge else res.json()
        self.parse(result)


if __name__ == '__main__':
    #  'https': 'https://58.47.159.147:8001'
    p = {
        # 'https': 'https://117.68.192.124:1133'
        'https': 'https://179.178.244.155:8081'
    }
    de = CrawlerBase()
    de.ip_verify(p)
