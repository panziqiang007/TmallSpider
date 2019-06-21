#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date        : 2019-06-21 14:13:40
# @Author      : Joson (joson1205@163.com)
# @Description : 更新商品ID

import os
import requests
import pymysql
import re
import time
import setting


class UpdateID(object):
    def __init__(self):
        self.con = pymysql.connect(
            setting.host,
            setting.user,
            setting.password,
            setting.database,
            cursorclass=pymysql.cursors.DictCursor)
        self.cur = self.con.cursor()
        self.run()
        self.cur.close()
        self.con.close()

    def run(self):
        self.get_mysql_item_id()
        print("已获取数据库id,开始更新全店商品ID")
        for item in self.item_list:
            # item = {shop_id,sellerNicl,BC_type,url,id[]}
            self.get_new_itemid(item)
        self.mysql_insert()

    def get_mysql_item_id(self):
        self.cur.execute("SELECT * FROM seller")
        self.item_list = self.cur.fetchall()
        self.cur.execute("SELECT item_id,shop_id FROM detail_info")
        listid = self.cur.fetchall()
        for item in self.item_list:
            item["id"] = []
            for id in listid:
                if item["shop_id"] == id["shop_id"]:
                    item["id"].append(id["item_id"])
        self.item_list

    def get_new_itemid(self, item):
        url = item["url"].split(".")[0] + ".m.tmall.com/shop/shop_auction_search.do?"
        s = requests.Session()
        s.headers = {
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Linux; Android 7.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Mobile Safari/537.36",
            "Accept": "*/*",
            "Referer": item["url"].split(".")[0] + ".m.tmall.com/shop/shop_auction_search.htm?sort=default",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        new_id = []
        page = 0
        total = 0
        while True:
            page += 1
            payload = {
                "sort": "s",
                "p": page,
                "from": "h5",
                "shop_id": item["shop_id"],
                "ajson": "1",
                "_tm_source": "tmallsearch"
            }
            response = s.get(url, params=payload).json()
            new_id = new_id + response["items"]
            print("获取<<{}>>第{}页ID".format(item["sellerNick"], page))
            if page == int(response["total_page"]):
                break
            time.sleep(5)
        # 拆分嵌套的列表,取ID值
        new_id = [str(new_id[i]["item_id"]) for i in range(len(new_id))]
        # id去重
        new_id = list(set(new_id))
        for id in item["id"]:
            if id in new_id:
                new_id.remove(id)
        item["new_id"] = new_id

    def mysql_insert(self):
        try:
            insert_list = []
            for item in self.item_list:
                while item["new_id"]:
                    _id = item["new_id"].pop()
                    insert_list.append((_id, item["shop_id"]))
            print("更新数据库商品id...")
            sql = "INSERT INTO detail_info (item_id,shop_id) VALUES (%s,%s)"
            self.cur.executemany(sql, insert_list)
            self.con.commit()
            print("共更新完成{}条记录!".format(len(insert_list)))
        except Exception as e:
            self.con.rollback()  # 事务回滚
            print('事务处理失败', e)


if __name__ == '__main__':
    UpdateID()
