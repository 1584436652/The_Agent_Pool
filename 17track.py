import requests
import json
import math
import time
import random
# import PySimpleGUI as sg
# from openpyxl import load_workbook
# from openpyxl import Workbook
from retry import retry

import cheer_config
from baidu_api import baidufanyi
from con_mysql import Connect_mysql
from share_func import now_time
from shipment_17track import CheerShipment
from Ua import ua


"""
17track查单
"""


class Track17(object):

    def __init__(self, cookies=None):
        # 用于excel存储
        self.number = 2
        # 操作excel
        # self.wb = Workbook()
        # self.ws = self.wb.active
        # self.ws.append(['track_number', '签收状态', '物流详情'])
        # # 文件存储名
        # self.file_location = '物流.xlsx'
        self.headers = {
            "user-agent": ua(),
            'Referer': 'https://t.17track.net/zh-cn',
            'Cookie': cookies
        }
        self.proxies = {
            # "https": "https://58.47.159.147:8001"
        }
        self.url = 'https://t.17track.net/restapi/track'

    # @property
    # def my_headers(self):
    #     user_agent = random.choice(self.headers_list)
    #     self.headers["user-agent"] = user_agent
    #     return self.headers

    # 读取跟踪号表格
    # def read_trcak(self, file_path):
    #     wb = load_workbook(file_path)
    #     ws = wb.active
    #     rows = []
    #     tracking_number_list = []
    #     for row in ws.iter_rows():
    #         rows.append(row)
    #     for x in range(1, len(rows)):
    #         # 物流跟踪号
    #         tracking_number = str(rows[x][0].value)
    #         # message = str(rows[x][1].value)
    #         # nation = str(rows[x][2].value)
    #         tracking_number_list.append(tracking_number)
    #     return tracking_number_list

    # 构造data
    def trcak_data(self, track_list: list, *args):
        messages = []
        for order in track_list[args[0]:args[1]]:
            result = {"num": order, "fc": 0, "sc": 0}
            messages.append(result)
        data = {
            "data": messages,
            "guid": "",
            "timeZoneOffset": -480
        }
        print(messages)
        return data

    @retry(delay=400)
    def make_response(self, url, headers, data):
        print(f'正在请求--{url}')
        # print(headers)
        response = requests.post(url=url, headers=headers, data=json.dumps(data), proxies=self.proxies)
        html_data = response.json()
        # print(html_data)
        if html_data['dat']:
            return html_data
        print("您的查询过于频繁，请稍后查询，等待重新尝试中(300s)...")
        raise Exception

    # 检查数据是否正确, ["track"]["e"]是否有数据，为None，需要重新请求
    @staticmethod
    def check_json_data(track_none):
        orders = track_none["dat"]
        try:
            for order in orders:
                if order["track"]["e"]:
                    continue
            return track_none
        except Exception:
            return None

    # 解析json获取物流信息
    @staticmethod
    def track_parse(track_json):
        parse = {}
        orders = track_json["dat"]
        for order in orders:
            # 跟踪号
            track_numbers = order["no"]
            # 物流状态
            delivery_status = str(order["track"]["e"])
            # print(track_numbers, delivery_status)
            # 最新的物流详情
            try:
                delivery_details = order["track"]["z0"]["z"]
                parse[track_numbers] = [delivery_status, delivery_details]
            except TypeError:
                parse[track_numbers] = [delivery_status, "No logistics details"]
        return parse

    # 修改解析后的物流状态
    @staticmethod
    def modify_status(messages: dict):
        status = {
            "0": "查询不到",
            "10": "运输途中",
            "35": "投递失败",
            "30": "到达待取",
            "40": "成功签收",
            "50": "可能异常",
            "60": "运输过久",
        }
        for message_key, massage_value in messages.items():
            # 把对应的物流状态改为中文
            messages[message_key][0] = status[messages[message_key][0]]
        return messages

    # 把modify_status列表转list便于excel和mysql一起储存，并翻译物流详情,添加当前时间
    @staticmethod
    def translate(translate_data):
        translate_list = []
        for key, values in translate_data.items():
            translate_list.append([key, values[0], baidufanyi(values[1]), now_time()])
        return translate_list

    # 保存为excel
    # def save_track_status(self, track_save):
    #     print(f'总条数：{len(track_save)}')
    #     for save_value in track_save:
    #         self.ws[f'A{self.number}'] = save_value[0]
    #         self.ws[f'B{self.number}'] = save_value[1]
    #         self.ws[f'C{self.number}'] = save_value[2]
    #         self.number += 1
    #     self.wb.save(self.file_location)
    #     print(f'已存储至:{self.file_location}')

    # 当前时间，做于文件名
    @property
    def date_name(self):
        return time.strftime("%Y%m%d", time.localtime(int(time.time())))

    # 选取文件
    # @property
    # def gui_choose_file(self):
    #     file_address = sg.popup_get_file('请选择你要读取的表格文件：')
    #     return file_address

    # 跟踪号条数/40向上取整
    def ceil_int(self, totals):
        return math.ceil(totals / 40)

    def main(self, track_list):
        # track_list = track.read_trcak('track.xlsx')
        totals = self.ceil_int(len(track_list))
        # 一次只能查找40条
        start_number = 0
        end_number = 40
        while totals >= 1:
            data = self.trcak_data(track_list, start_number, end_number)
            track_json = self.make_response(self.url, self.headers, data)
            check = self.check_json_data(track_json)
            if check is not None:
                print(f"{start_number}-{end_number}物流详情获取成功")
                messages = self.track_parse(check)
                modify_data = self.modify_status(messages)
                all_data = self.translate(modify_data)
                # self.save_track_status(all_data)
                con.update_shipment('track_listing', all_data)

            else:
                while True:
                    print(f"{start_number}-{end_number}数据缺失，再次请求")
                    time.sleep(random.randint(20, 25))
                    track_json = self.make_response(self.url, self.headers, data)
                    check = self.check_json_data(track_json)
                    if check is not None:
                        print(f"{start_number}-{end_number}物流详情获取成功")
                        messages = self.track_parse(check)
                        modify_data = self.modify_status(messages)
                            all_data = self.translate(modify_data)
                        # self.save_track_status(all_data)
                        con.update_shipment('track_listing', all_data)
                        break

            start_number += 40
            end_number += 40
            totals -= 1
            if totals != 0:
                time.sleep(random.randint(20, 30))


if __name__ == '__main__':
    con = Connect_mysql('track')
    con.get_connect()
    # ship = CheerShipment()
    # track_list = ship.main()
    track_list = ['PBWM1400682750012040017500', 'PBWM1400685230017227017500']
    cookie = cheer_config.COOKIE
    track = Track17(cookie)
    track.main(track_list)
    con.close_mysql()
