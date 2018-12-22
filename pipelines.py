# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import psycopg2

# PostgreSQLへの保存
# PipelineはSpiderから抽出したItemに対して任意の処理を行うためのコンポーネント
# SpiderでyieldしたItemはすべてのPipelineを通過する
class PostgresPipeline(object):

    # Spider開始時の処理
    def open_spider(self, spider):
        # コネクションの開始
        url = spider.settings.get('POSTGRESQL_URL')
        self.conn = psycopg2.connect(url)

    # Spiderで取得した1Itemごとに処理
    def process_item(self, item, spider):
        sql = "INSERT INTO test_products(product_name, product_price, product_url) VALUES (%s, %s, %s)"

        curs = self.conn.cursor()
        curs.execute(sql, (item['product_name'], item['product_price'], item['product_url']))
        self.conn.commit()

        return item


    # Spider終了時の処理
    def close_spider(self, spider):
        # コネクションの終了
        self.conn.close()

