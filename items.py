# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class Headline(scrapy.Item):
    """
    Yahooニュースのヘッドラインを表すItem
    """

    title = scrapy.Field()
    body = scrapy.Field()
