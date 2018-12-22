import re
import json

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from myproject.mercari_items import Product

# CrawlSpider makes me easy to get URL infomation
class MercariSpider(CrawlSpider):

    #We can execute this program by "scrapy crawl mercari63 -o (filename).jl"

    name = 'mercari63'                                              #Spyder's name, we call the name in terminal
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
        item = Product()
        item['product_name']    = response.css('title::text').extract_first()                       #商品名
        #jsondata = response.xpath('//script[contains(., "application")]//text()')  #json
        #jsondata = response.xpath('//script//text()')
        #jsondata = json.loads(response.body)
        #datajson = json.dumps(jsondata)
        jsondata = response.xpath('//script[@type="application/ld+json"]/text()').extract_first()
        jsondata = json.loads(json.dumps(jsondata)).strip()
        index_price = jsondata.index("\"offers\": {")
        maindata_str = jsondata[:-(len(jsondata)-index_price)-8] + "\n     }"
        pricedata_str = "{" + jsondata[index_price+11:-1]
        #print(maindata_str)
        print(maindata_str)
        #maindata_json = json.loads(maindata_str)
        index_nonedot = maindata_str.index("\"name\":")-7
        index_name = maindata_str.index("\"name\":")
        strA = maindata_str[:-(len(maindata_str)-index_nonedot)]
        strB = maindata_str[index_name:]

        maindata_str2 = strA + ",\n      " + strB
        print(maindata_str2)

        maindata_json = json.loads(maindata_str2)
        print(maindata_json)
        print(type(maindata_json))

        pricedata_json = json.loads(pricedata_str)
        print(pricedata_json)
        print(type(pricedata_json))
        # print(maindata_str2)
        # maindata_json = json.loads(maindata_str)
        # print(type(maindata_json))
        # for jsondata in maindata_json.items():
        #     print(jsondata)

        for jsondata in pricedata_json.items():
            print(jsondata)

        #listjson = jsondata_loaded.split(": \"")
        #print(listjson)
        #print(jsondata_loaded)
        #print(type(jsondata_loaded))
        #jsondata_loaded2 = json.loads(jsondata_loaded)
        #print(jsondata_loaded2)
        #print(type(jsondata_loaded2))
        #for jsondata in jsondata_loaded.items():
        #    print(jsondata)

        #print(item['product_name'])
        #item['product_price'] = response.css('.tems-box-price font-5').xpath('string()').extract_first() #XPath allows me to get all text by tag
        yield item
