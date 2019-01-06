import re
import json

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from myproject.mercari_items import Product

# CrawlSpider makes me easy to get URL infomation
class MercariSpider(CrawlSpider):

    #We can execute this program by "scrapy crawl mercari63 -o (filename).jl"
    # 対象商品：『もし高校野球の女子マネージャーがドラッカーの『マネジメント』を読んだら』
    start_urls = ['https://www.mercari.com/jp/search/?keyword=%E3%82%82%E3%81%97%E9%AB%98%E6%A0%A1%E9%87%8E%E7%90%83%E3%81%AE%E5%A5%B3%E5%AD%90%E3%83%9E%E3%83%8D%E3%83%BC%E3%82%B8%E3%83%A3%E3%83%BC%E3%81%8C%E3%83%89%E3%83%A9%E3%83%83%E3%82%AB%E3%83%BC%E3%81%AE%E3%80%8E%E3%83%9E%E3%83%8D%E3%82%B8%E3%83%A1%E3%83%B3%E3%83%88%E3%80%8F%E3%82%92%E8%AA%AD%E3%82%93%E3%81%A0%E3%82%89']
    name = 'mercari'                                                #Spyder's name, we call the name in terminal
    allowed_domains = ['www.mercari.com','item.mercari.com']        #prevent unintentionally access

    # リンクをたどるルールリストを定義
    rules = (
            #各アイテムのリンクをたどりレスポンスを処理する
            Rule(LinkExtractor(allow=r'https://item.mercari.com/jp/m\d+/'), callback='parse_topics')
        ,
    )

    def parse_topics(self, response):
        """
        リンクごとに商品詳細ページにアクセスして情報を取得する
        """
        
        #商品情報を保持するitemクラスを定義
        item = Product()

        #商品情報JSONの取得
        product_rawinfo = response.xpath('//script[@type="application/ld+json"]/text()').extract_first()
        product_info_str = json.loads(json.dumps(product_rawinfo)).strip()
        product_dict = self.transform_jsonstr_to_dict(product_info_str)

        #商品情報JSON以外の取得
        #商品の評価
        XPATH_USER_RAING = '//div/div[@class="item-user-ratings"]/span/text()'
        user_rating_list = response.xpath(XPATH_USER_RAING).extract()
        rating_good_number = user_rating_list[0]    # Good
        rating_normal_number = user_rating_list[1]  # Normal
        rating_bad_number = user_rating_list[2]     # Bad

        #商品の状態
        XPATH_PRODUCT_STATUS = '//table/tr[4]/td[1]/text()'
        product_status = response.xpath(XPATH_PRODUCT_STATUS).extract_first()

        #配送料の負担
        XPATH_COST = '//table/tr[5]/td[1]/text()'
        cost_allocation = response.xpath(XPATH_COST).extract_first()

        #配送方法
        XPATH_DELIVER = '//table/tr[6]/td[1]/text()'
        way_to_deliver = response.xpath(XPATH_DELIVER).extract_first()

        #発送元
        XPATH_SHIP_FROM = '//table/tr[7]/td[1]/a/text()'
        ship_from = response.xpath(XPATH_SHIP_FROM).extract_first()  

        #発送日の目安
        XPATH_SHIPPING_DATE = '//table/tr[8]/td[1]/text()'
        shipping_date = response.xpath(XPATH_SHIPPING_DATE).extract_first()  

        #商品の説明
        XPATH_DESCRIPTION = '//p[@class="item-description-inner"]/text()'
        product_description = response.xpath(XPATH_DESCRIPTION).extract_first()  

        #いいね
        XPATH_LIKE_NUMBER = '//span[@data-num="like"]/text()'
        product_likes = response.xpath(XPATH_LIKE_NUMBER).extract_first() 

        #販売ステータス
        XPATH_NOW_ON_SALE = '//section[@class="visible-sp"]//div/text()'
        now_on_sale = response.xpath(XPATH_NOW_ON_SALE).extract_first() 

        #ハッシュタグ
        #TODO

        #Productクラスにデータを格納
        item['product_name']        = product_dict['name']
        item['product_price']       = product_dict['price']
        item['product_image_url']   = product_dict['image']
        item['product_url']         = product_dict['url']

        item['rating_good']         = rating_good_number
        item['rating_normal']       = rating_normal_number
        item['rating_bad']          = rating_bad_number

        item['product_status']      = product_status
        item['cost_allocation']     = cost_allocation
        item['way_to_deliver']      = way_to_deliver
        item['ship_from']           = ship_from
        item['shipping_date']       = shipping_date

        item['product_description'] = product_description
        item['product_likes']       = product_likes
        item['now_on_sale']         = now_on_sale
        
        yield item

    # JSON文字列を処理する関数
    def transform_jsonstr_to_dict(self, product_info_str_):
        """
        Mercariの各商品ページに埋め込まれたJSONをもとに商品情報をdict化するメソッド
        """
        #メインデータ部分(金額以外)の文字列整形
        index_price = product_info_str_.index("\"offers\": {")
        index_maindata = len(product_info_str_)-index_price + 8
        maindata_str = product_info_str_[:-index_maindata] + "\n     }"

        #価格部分の文字列整形
        index_pricestart = index_price+11
        pricedata_str = "{" + product_info_str_[index_pricestart:-1]

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

        maindata_dict['price'] = pricedata_dict['price']

        return maindata_dict

