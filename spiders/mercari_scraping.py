import re
import json

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from myproject.mercari_items import Product

# CrawlSpider makes me easy to get URL infomation
class MercariSpider(CrawlSpider):

    #We can execute this program by "scrapy crawl mercari63 -o (filename).jl"

    name = 'mercari'                                            #Spyder's name, we call the name in terminal
    allowed_domains = ['www.mercari.com','item.mercari.com']        #prevent unintentionally access
    start_urls = ['https://www.mercari.com/jp/category/5/']         #Mercari site(product list page)

    # リンクをたどるルールリストを定義
    rules = (
        #各アイテムのリンクをたどりレスポンスを処理する
        Rule(LinkExtractor(allow=r'https://item.mercari.com/jp/m\d+/'), callback='parse_topics')
        ,
    )

    # リンクごとに詳細ページにアクセスして情報を取得する
    def parse_topics(self, response):
        """
        トピックスのページからタイトルと本文を抜き出す
        """
        
        #商品情報を保持するScrapyクラスを定義
        item = Product()
        #item['product_name']    = response.css('title::text').extract_first()   #商品名

        #商品情報JSONの取得
        product_rawinfo = response.xpath('//script[@type="application/ld+json"]/text()').extract_first()
        product_info_str = json.loads(json.dumps(product_rawinfo)).strip()
        print(product_info_str)

        #メインデータ部分(金額以外)の文字列整形
        index_price = product_info_str.index("\"offers\": {")
        index_maindata = len(product_info_str)-index_price + 8
        maindata_str = product_info_str[:-index_maindata] + "\n     }"

        #価格部分の文字列整形
        index_pricestart = index_price+11
        pricedata_str = "{" + product_info_str[index_pricestart:-1]

        #メインデータ部分
        index_name = maindata_str.index("\"name\":")
        index_noncomme = index_name-7
        index_pricedata = len(maindata_str)-index_noncomme
        before_noncomme = maindata_str[:-index_pricedata]
        after_noncomme = maindata_str[index_name:]
        maindata_str = before_noncomme + "\n      " + after_noncomme    #Mercari側のソースが修正されたため,不要

        #JSON文字列を辞書型に変換
        maindata_dict = json.loads(maindata_str)
        pricedata_dict = json.loads(pricedata_str)

        #Productクラスにデータを格納
        item['product_name'] = maindata_dict['name']
        item['product_price'] = pricedata_dict['price']
        item['product_image'] = maindata_dict['image']
        item['product_url'] = maindata_dict['url']
    
        yield item
