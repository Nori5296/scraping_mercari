import scrapy
from myproject.mercari_items import Product

class MerSpider(scrapy.Spider):
    name = 'mercari'                        #Spyder's name
    allowed_domains = ['www.mercari.com','item.mercari.com']   #prevent unintentionally access
    start_urls = ['https://www.mercari.com/jp/category/5/']

    def parse(self, response):
        """
        個々のトピックスへのリンクを抜き出して表示する
        """
        for url in response.css('section.items-box a::attr("href")').re(r'https://item.mercari.com/jp/m\d+/'):   #only get text by ::
            #Callback Func against Response is the second variable
            print(url)
            yield scrapy.Request(url, self.parse_topics)  #yield is like a return, urljoin for revise url in case of relative url

    def parse_topics(self, response):
        """
        トピックスのページからタイトルと本文を抜き出す
        """
        item = Product()
        print("parse_topics now")
        #print(response.css('title::text').extract_first())
        item['product_name'] = response.css('title::text').extract_first()   #???
        #print(item['product_name']) #???
        #item['product_price'] = response.css('.tems-box-price font-5').xpath('string()').extract_first() #XPath allows me to get all text by tag
        yield item

