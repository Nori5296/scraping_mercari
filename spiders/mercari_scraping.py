import re
import json

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from myproject.mercari_items import Product
from myproject.functions.initialize import url_list_generator

class MercariSpider(CrawlSpider):
    """メルカリから商品情報を取得するクロールスパイダー
    """
    #We can execute this program by "scrapy crawl mercari63 -o (filename).jl"
    # 対象商品：『もし高校野球の女子マネージャーがドラッカーの『マネジメント』を読んだら』
    name = 'mercari'
    allowed_domains = ['www.mercari.com','item.mercari.com']
    start_urls = url_list_generator()

    # リンクをたどるルールリストを定義
    rules = (
            #各アイテムのリンクをたどりレスポンスを処理する
            Rule(LinkExtractor(allow=r'https://item.mercari.com/jp/m\d+/'
                                , restrict_xpaths='//div[@class="items-box-content clearfix"]/section[@class="items-box"]')
                                , callback='parse_topics'),
    )

    def parse_topics(self, response):
        """リンクごとに商品詳細ページにアクセスして情報を取得する
        """

        print("URL: " + response.request.url)
        
        #商品情報を保持するitemクラスを定義
        item = Product()

        #商品情報JSONの取得
        product_rawinfo = response.xpath('//script[@type="application/ld+json"]/text()').extract_first()
        product_info_str = json.loads(json.dumps(product_rawinfo)).strip()
        product_json_dict = self.transform_jsonstr_to_dict(product_info_str)

        #商品情報JSON以外の取得
        #商品の評価
        XPATH_USER_RAING = '//div/div[@class="item-user-ratings"]/span/text()'
        user_rating_list = response.xpath(XPATH_USER_RAING).extract()
        rating_good_number = user_rating_list[0]    # Good
        rating_normal_number = user_rating_list[1]  # Normal
        rating_bad_number = user_rating_list[2]     # Bad

        # 商品情報取得クラスをインスタンス化
        productInfoService = ProductInfoService(response)
        product_dict = productInfoService.get_product_info_dict()

        #ハッシュタグ
        # TODO: 修正
        # hash_list = productInfoService.hash_list_creator()

        # for hashtag in hash_list:
        #     print("Hash:" + hashtag + "\n")

        #Productクラスにデータを格納
        item['product_name']        = product_json_dict['name']
        item['product_price']       = product_json_dict['price']
        item['product_image_url']   = product_json_dict['image']
        item['product_url']         = product_json_dict['url']

        item['rating_good']         = rating_good_number
        item['rating_normal']       = rating_normal_number
        item['rating_bad']          = rating_bad_number

        item['product_status']      = product_dict['product_status']
        item['cost_allocation']     = product_dict['cost_allocation']
        item['way_to_deliver']      = product_dict['way_to_deliver']
        item['ship_from']           = product_dict['ship_from']
        item['shipping_date']       = product_dict['shipping_date']

        item['product_description'] = product_dict['product_description']
        item['product_likes']       = product_dict['product_likes']
        item['now_on_sale']         = product_dict['now_on_sale']
        
        yield item


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


class ProductInfoService():
    """レスポンスをもとに商品データを取得する
    """

    XPATH_PRODUCT_STATUS = '//table/tr[4]/td[1]/text()'
    XPATH_COST = '//table/tr[5]/td[1]/text()'
    XPATH_DELIVER = '//table/tr[6]/td[1]/text()'
    XPATH_SHIP_FROM = '//table/tr[7]/td[1]/a/text()'
    XPATH_SHIPPING_DATE = '//table/tr[8]/td[1]/text()'
    XPATH_DESCRIPTION = '//p[@class="item-description-inner"]/text()'
    XPATH_LIKE_NUMBER = '//span[@data-num="like"]/text()'
    XPATH_NOW_ON_SALE = '//section[@class="visible-sp"]//div/text()'
    
    __response = None
    __product_status = None
    __cost_allocation = None
    __way_to_deliver = None
    __ship_from = None
    __shipping_date = None
    __product_description = None
    __product_likes = None
    __now_on_sale = None

    def __init__(self, response):

        self.__product_status = response.xpath(self.XPATH_PRODUCT_STATUS).extract_first()   #商品の状態
        self.__cost_allocation = response.xpath(self.XPATH_COST).extract_first()            #配送料の負担
        self.__way_to_deliver = response.xpath(self.XPATH_DELIVER).extract_first()          #配送方法
        self.__ship_from = response.xpath(self.XPATH_SHIP_FROM).extract_first()             #発送元
        self.__shipping_date = response.xpath(self.XPATH_SHIPPING_DATE).extract_first()     #発送日の目安
        self.__product_description = response.xpath(self.XPATH_DESCRIPTION).extract_first() #商品の説明
        self.__product_likes = response.xpath(self.XPATH_LIKE_NUMBER).extract_first()       #いいね
        self.__now_on_sale = response.xpath(self.XPATH_NOW_ON_SALE).extract_first()         #販売ステータス

    def get_product_info_dict(self):
        """商品情報を辞書型で返却する
        """
        ret_dict = {}
        ret_dict['product_status'] = self.__product_status
        ret_dict['cost_allocation'] = self.__cost_allocation
        ret_dict['way_to_deliver'] = self.__way_to_deliver
        ret_dict['ship_from'] = self.__ship_from
        ret_dict['shipping_date'] = self.__shipping_date
        ret_dict['product_description'] = self.__product_description
        ret_dict['product_likes'] = self.__product_likes
        ret_dict['now_on_sale'] = self.__now_on_sale

        return ret_dict

    def hash_list_creator(self):
        """商品説明からハッシュタグを抽出する
        """
        #TODO: 修正
        product_text = self.__product_description
        hash_list = re.findall(r'#.+\s', product_text)

        return hash_list
