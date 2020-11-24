import scrapy
import logging
from scrapy.loader import ItemLoader
from six.moves.urllib.parse import urljoin
from scrapy.http import FormRequest
from scrapy.exceptions import CloseSpider
from ..items import FacebookSpiderItem

class FacebookSpider(scrapy.Spider):
    name = 'test'
    start_urls = ['https://mbasic.facebook.com/DonaldTrump']

    def parse(self, response):
        items = FacebookSpiderItem()
        all_div_quotes = response.css('div.ej')
        for quotes in all_div_quotes:
            title = quotes.css('p').extract()
            items['title'] = title
            print(title)
            yield items