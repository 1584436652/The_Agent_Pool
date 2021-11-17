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
            # print(dicts)
            yield self.ip_verify(dicts)
            time.sleep(10)


if __name__ == '__main__':
    zdy = ZDYProxy()
    params = {"https": 1}
    dats = zdy.run(url=zdy.url_ip, method='GET', headers=zdy.headers, params=params, proxies=zdy.proxies)
    for dat in dats:
        zdy.ip_save_to_mongodb(dat)
