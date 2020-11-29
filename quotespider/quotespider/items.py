# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class QuotetutorialItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    tag = scrapy.Field()

class FacebookSpiderItem(scrapy.Item):
    title = scrapy.Field()
    page = scrapy.Field()
    search_id = scrapy.Field()
