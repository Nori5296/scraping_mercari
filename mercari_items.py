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
    rating_good = scrapy.Field()
    rating_normal = scrapy.Field()
    rating_bad = scrapy.Field()
    product_status = scrapy.Field()
    cost_allocation = scrapy.Field()
    way_to_deliver = scrapy.Field()
    ship_from = scrapy.Field()
    shipping_date = scrapy.Field()
    product_description = scrapy.Field()
    product_likes = scrapy.Field()