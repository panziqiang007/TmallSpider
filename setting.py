#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date        : 2019-06-21 11:34:41
# @Author      : Joson (joson1205@163.com)
# @Description : 数据库配置

import pymysql
import update_itemID

host = "ip"
user = "root"
password = "123456"
database = "test_db"

#======================
# 首次执行,需配置数据库
#======================


class CreatTbale(object):
    """docstring for CreatTbale"""

    def __init__(self):
        self.con = pymysql.connect(host, user, password, database)
        self.cur = self.con.cursor()
        self.run()
        self.cur.close()
        self.con.close()
        print("Done!")

    def seller(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS `seller`(
                    `shop_id` varchar(20) NOT NULL,
                    `sellerNick` varchar(50) NOT NULL,
                    `BC_type` varchar(10) DEFAULT NULL,
                    `url` varchar(255) DEFAULT NULL,
                    PRIMARY KEY (`shop_id`),
                    UNIQUE KEY `shop_id` (`shop_id`) USING BTREE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
            """)
        self.con.commit()

    def detail_info(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS `detail_info` (
                    `item_id` varchar(20) NOT NULL COMMENT '商品id',
                    `shop_id` varchar(20) DEFAULT NULL,
                    `title` varchar(100) DEFAULT NULL,
                    `ArtNo` varchar(50) DEFAULT NULL COMMENT '货号',
                    `sku` longtext,
                    `texture` varchar(255) DEFAULT NULL COMMENT '材质',
                    `categoryId` varchar(20) DEFAULT NULL COMMENT '类目id',
                    `rootCategoryId` varchar(25) DEFAULT NULL COMMENT '一级目录',
                    `commentCount` int(11) DEFAULT NULL COMMENT '评价数',
                    `sellCount` int(11) DEFAULT NULL COMMENT '销量',
                    `favcount` int(11) DEFAULT NULL COMMENT '收藏数',
                    `price` decimal(10,2) DEFAULT NULL,
                    `item_status` varchar(20) DEFAULT NULL COMMENT '商品状态,默认值:可售',
                    `max_price` decimal(10,2) DEFAULT NULL,
                    `min_price` decimal(10,2) DEFAULT NULL,
                    `update_time` datetime DEFAULT NULL COMMENT '数据更新时间',
                    PRIMARY KEY (`item_id`),
                    UNIQUE KEY `item_id` (`item_id`) USING BTREE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
            """)
        self.con.commit()

    def run(self):
        self.seller()
        self.detail_info()


if __name__ == '__main__':
    CreatTbale()
    update_itemID.UpdateID()
