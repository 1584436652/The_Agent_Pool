from lxml import etree
from crawler_base import CrawlerBase

"""
89代理
"""


class IPAddressPool(CrawlerBase):

    def __init__(self):
        super().__init__()
        self.url89 = 'https://www.89ip.cn/index_{}.html'

    def parse(self, res):
        dicts = {}
        html = etree.HTML(res)
        result = html.xpath('//table[@class="layui-table"]//tbody//tr')
        for i in result:
            ip = i.xpath('./td[1]/text()')[0].strip()
            port = i.xpath('./td[2]/text()')[0].strip()
            dicts[ip] = port
        return dicts

    def run(self):
        for page in range(1, 10):
            url = self.url89.format(page)
            res = self.make_response(url)
            data_dicts = self.parse(res)
            for ip, port in data_dicts.items():
                print('{0}:{1}'.format(ip, port))
                self.ip_detection(ip, port)

    def ip_save_to_mongodb(self):
        pass


if __name__ == '__main__':
    de = IPAddressPool()
    de.run()