import requests
from pymongo import MongoClient
from retry import retry

from Ua import ua


class CrawlerBase(object):

    def __init__(self):
        self.headers = {
            'User-Agent': ua(),
            'Referer': 'https://www.zdaye.com/free/'
                       '?ip=&adr=&checktime=&sleep=&cunhuo=&dengji=&nadr=&https=1&yys=&post=&px=',
            # 'Host': 'www.zdaye.com'
        }
        self.proxies = {
            'https': 'https://113.238.142.208:3128'
        }
        # mongodb数据库操作对象
        self.client = MongoClient(host='127.0.0.1', port=27017)
        # 数据插⼊的数据库与集合
        self.coll = self.client["IP"]["IPAddressPool"]

    @retry(tries=3, delay=3)
    def make_response(self, url, method=None, timeout=None, **kwargs):
        _method = "GET" if not method else method
        _maxTimeout = timeout if timeout else 3
        print(f'正在请求-----')
        try:
            response = requests.request(method=_method, url=url, timeout=_maxTimeout, **kwargs)
            print(response.status_code)
            assert response.status_code == 200
            return response
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ProxyError) as e:
            raise e

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
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ProxyError):
            print(f"{proxies}请求超时，代理无效！！！")
            return None

    @staticmethod
    def save_csv(self, text):
        with open('proxies_ip.csv', 'a', encoding='utf-8') as f:
            f.write(text)

    def ip_save_to_mongodb(self, items):
        for k, v in items:
            self.coll.update({"代理ip": v}, True)

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
    p = {'https': 'https://120.52.73.105:18080'}
    de = CrawlerBase()
    de.ip_verify(p)
