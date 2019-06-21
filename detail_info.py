#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date        : 2019-06-21 11:34:41
# @Author      : Joson (joson1205@163.com)
# @Description : 获取天猫单品数据

import requests
import time
import setting
import pymysql


class GetDetail(object):
    def __init__(self):
        self.con = pymysql.connect(
            setting.host,
            setting.user,
            setting.password,
            setting.database)
        self.cur = self.con.cursor()
        self.item_list = self.get_mysql_item_id()
        self.result = []
        self.start()
        self.mysql_insert()
        self.cur.close()
        self.con.close()

    def get_mysql_item_id(self):
        self.cur.execute("SELECT item_id FROM detail_info")
        data = self.cur.fetchall()
        data = [data[i][0] for i in range(len(data))]
        return data

    def start(self):
        while self.item_list:
            self.item_id = self.item_list.pop()
            self.data = {}
            self.data["item_id"] = self.item_id
            # 预设值
            self.data["shop_id"] = "None"
            self.data["title"] = "None"
            self.data["ArtNo"] = "None"
            self.data["sku"] = "None"
            self.data["texture"] = "None"
            self.data["categoryId"] = "None"
            self.data["rootCategoryId"] = "None"
            self.data["item_status"] = "sellable"
            self.data["update_time"] = time.strftime("%Y-%m-%d %X", time.localtime())
            self.data["price"] = 0
            self.data["max_price"] = 0
            self.data["min_price"] = 0
            self.data["commentCount"] = 0
            self.data["sellCount"] = 0
            self.data["favcount"] = 0
            self.basic(self.item_id)
            if self.data["sku"] == "None":
                self.data["item_status"] = "unsellable"
            self.result.append(self.data)
            time.sleep(5)

    def basic(self, item_id):
        url = "https://h5api.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4"}
        data = {
            "v": "6.0",
            "type": "jsonp",
            "ttid": "2017@taobao_h5_6.6.0",
            "t": int(time.time()),
            "sign": "55a77e2aae8dcb7604b2e4150c611d37",
            "jsv": "2.4.8",
            "dataType": "jsonp",
            "data": "{\"itemNumId\":\"" + item_id + "\"}",
            "appKey": "12574478",
            "api": "mtop.taobao.detail.getdetail",
            "AntiCreep": "true"}
        s = requests.session()
        response = s.get(url, headers=headers, params=data).json()
        print("id:{}->>{}".format(item_id, response["ret"][0]))
        try:
            self.data["sellerNick"] = response["data"]["seller"]["sellerNick"]
            self.data["shop_id"] = response["data"]["seller"]["shopId"]
            self.data["BC_type"] = response["data"]["seller"]["sellerType"]
            self.data["favcount"] = response["data"]["item"]["favcount"]
            self.data["title"] = response["data"]["item"]["title"]
            self.data["commentCount"] = response["data"]["item"]["commentCount"]
            self.data["categoryId"] = response["data"]["item"]["categoryId"]
            self.data["rootCategoryId"] = response["data"]["item"]["rootCategoryId"]
            # 商品属性信息是多层嵌套列表
            props = response["data"]["props"]["groupProps"]
            while props:
                dict_1 = props.pop()
                if "基本信息" in dict_1.keys():
                    while dict_1["基本信息"]:
                        dict_2 = dict_1["基本信息"].pop()
                        if "货号" in dict_2.keys():
                            self.data["ArtNo"] = dict_2["货号"]
                        elif "材质成分" in dict_2.keys():
                            self.data["texture"] = dict_2["材质成分"]
                        else:
                            pass
            skuData = eval(response["data"]["apiStack"][0]["value"])
            self.sku_info(skuData)
        except Exception as e:
            print(e)

    def sku_info(self, skuData):
        self.data["sellCount"] = skuData["item"]["sellCount"]
        # 默认显示价格(存在价格区间则选最小的)
        p = skuData["skuCore"]["sku2info"]["0"]["price"]["priceText"].split("-")
        self.data["price"] = round(float(p[0]), 2)
        sku_price = []
        skuBase = {}
        skuCore = skuData["skuCore"]["sku2info"]
        # 只获取库存大于0的SKU
        for k in skuCore.keys():
            if k != "0" and int(skuCore[k]["quantity"]) > 0:
                skuBase[k] = {}
                sku_price.append(round(float(skuCore[k]["price"]["priceText"]), 2))

        self.data["max_price"] = max(sku_price)
        self.data["min_price"] = min(sku_price)

        while skuData["skuBase"]["skus"]:
            skuid = skuData["skuBase"]["skus"].pop()
            if skuid["skuId"] in skuBase.keys():
                skuBase[skuid["skuId"]]["propPath"] = skuid["propPath"]

        sku_zh = ""
        for key in skuBase.keys():
            propPath = skuBase[key]["propPath"].split(";")
            for i in range(len(propPath)):
                propPath2 = propPath[i].split(":")
                for i2 in range(len(skuData["skuBase"]["props"])):
                    if propPath2[0] == skuData["skuBase"]["props"][i2]["pid"]:
                        for i3 in range(len(skuData["skuBase"]["props"][i2]["values"])):
                            if propPath2[1] == skuData["skuBase"]["props"][i2]["values"][i3]["vid"]:
                                sku_zh = sku_zh + str(skuData["skuBase"]["props"][i2]["values"][i3]["name"])
            sku_zh = sku_zh + ";"
        # 写入
        self.data["sku"] = sku_zh

    def mysql_insert(self):
        try:
            print("开始写入数据库...")
            self.mysql_del()
            insert_list = []
            while self.result:
                item = self.result.pop()
                insert_list.append((
                    item["item_id"],
                    item["shop_id"],
                    item["title"],
                    item["ArtNo"],
                    item["sku"],
                    item["texture"],
                    item["categoryId"],
                    item["rootCategoryId"],
                    item["commentCount"],
                    item["sellCount"],
                    item["price"],
                    item["max_price"],
                    item["min_price"],
                    item["favcount"],
                    item["item_status"],
                    item["update_time"]
                ))
            table_content = (r"%s," * 16)[:-1]
            sql = """
                INSERT INTO detail_info (
                            item_id,
                            shop_id,
                            title,
                            ArtNo,
                            sku,
                            texture,
                            categoryId,
                            rootCategoryId,
                            commentCount,
                            sellCount,
                            price,
                            max_price,
                            min_price,
                            favcount,
                            item_status,
                            update_time
                            ) VALUES ({})
                """.format(table_content)
            self.cur.executemany(sql, insert_list)
            self.con.commit()
            print("数据写入完成!")
        except Exception as e:
            self.con.rollback()  # 事务回滚
            print('事务处理失败', e)

    def mysql_del(self):
        self.cur.execute("DELETE FROM detail_info")
        self.con.commit()


if __name__ == '__main__':
    GetDetail()
