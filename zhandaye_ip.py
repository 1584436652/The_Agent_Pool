import time

from lxml import etree
from crawler_base import CrawlerBase


"""
站大爷代理
"""


class ZDYProxy(CrawlerBase):

    def __init__(self):
        super(ZDYProxy, self).__init__()
        self.url_ip = 'https://www.zdaye.com/Free/'

    def parse(self, res):
        html = etree.HTML(res)
        result = html.xpath('//table[@id="ipc"]/tbody/tr')
        for i in result:
            dicts = {}
            ip = i.xpath('./td[1]/text()')[0]
            port = i.xpath('./td[2]/text()')[0]
            dicts["https"] = f"https://{ip}:{port}"
            yield self.ip_verify(dicts)
            time.sleep(5)

    def run(self):
        params = {"https": 1}
        p = {
            'https': 'https://117.161.75.82:3128'
        }
        res = self.make_response(method='GET', url=self.url_ip, headers=self.headers, params=params, proxies=p)
        print(res.text)
        text = self.parse(res.text)
        print(res.text)
        self.save_csv(text)


if __name__ == '__main__':
    de = ZDYProxy()
    de.run()
