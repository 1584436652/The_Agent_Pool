import time

from lxml import etree
from crawler_base import CrawlerBase


"""
站大爷代理
"""


class ZDYProxy(CrawlerBase):

    def __init__(self):
        super(ZDYProxy, self).__init__()
        self.url_ip = ['https://www.zdaye.com/Free/{}'.format(page) for page in range(1, 4)]

    def parse(self, res):
        html = etree.HTML(res)
        result = html.xpath('//table[@id="ipc"]/tbody/tr')
        for i in result:
            dicts = {}
            ip = i.xpath('./td[1]/text()')[0]
            port = i.xpath('./td[2]/text()')[0]
            # network_https = i.xpath('./td[6]/div')
            # # network_post = i.xpath('./td[7]/div')
            # if network_https:
            #     network_type = "https"
            dicts["https"] = f"https://{ip}:{port}"
            # print(dicts)
            yield self.ip_verify(dicts)


if __name__ == '__main__':
    zdy = ZDYProxy()
    params = {"https": 1}
    pro = {}
    for url in zdy.url_ip:
        print(url)
        dats = zdy.run(url=url, method='GET', headers=zdy.headers, params=params, proxies=pro)
        for dat in dats:
            if dat:
                print(dat)
                zdy.ip_save_to_mongodb(dat)
