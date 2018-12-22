import scrapy
from myproject.items import Headline

class NewsSpider(scrapy.Spider):
    name = 'news'   #Spyder's name
    allowed_domains = ['news.yahoo.co.jp'] #prevent unintentionally access
    start_urls = ['http://news.yahoo.co.jp/']

    def parse(self, response):
        """
        個々のトピックスへのリンクを抜き出して表示する
        """
        for url in response.css('ul.topics a::attr("href")').re(r'/pickup/\d+$'):   #only get text by ::
            #Callback Func against Response is the second variable
            yield scrapy.Request(response.urljoin(url), self.parse_topics)  #yield is like a return

    def parse_topics(self, response):
        """
        トピックスのページからタイトルと本文を抜き出す
        """
        item = Headline()
        item['title'] = response.css('.newsTitle ::text').extract_first()   
        item['body'] = response.css('.hbody').xpath('string()').extract_first() #XPath allows me to get all text by tag
        yield item

