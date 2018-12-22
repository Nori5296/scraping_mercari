# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class Product(scrapy.Item):
    """
    メルカリの1商品を表すItem
    """

    product_name = scrapy.Field()
    product_price = scrapy.Field()
    product_image = scrapy.Field()
    product_url = scrapy.Field()

