import time
from lxml import etree

from crawler_base import CrawlerBase

"""
快代理
"""


class KDLProxy(CrawlerBase):
    def __init__(self):
        super(KDLProxy, self).__init__()
        self.kdl_url = "https://www.kuaidaili.com/free/"

    def parse(self, res):
        html = etree.HTML(res)
        items = html.xpath('//div[@id="list"]/table/tbody/tr')
        for item in items:
            dicts = {}
            ip = item.xpath('./td[1]/text()')[0]
            port = item.xpath('./td[2]/text()')[0]
            proxy_type = item.xpath('./td[4]/text()')[0]
            print(ip, port, proxy_type)
            if proxy_type == "HTTP":
                dicts["http"] = f"https://{ip}:{port}"
            else:
                dicts["https"] = f"https://{ip}:{port}"
            print(dicts)
            self.ip_verify(dicts)
            time.sleep(5)


if __name__ == '__main__':
    kdl = KDLProxy()
    proxies = {
        'https': 'https://58.47.159.147:8001'
    }
    kdl.run('GET', kdl.headers,  url=kdl.kdl_url, proxies=proxies)

