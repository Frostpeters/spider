import scrapy
import logging
from scrapy.loader import ItemLoader
from six.moves.urllib.parse import urljoin
from scrapy.http import FormRequest
from scrapy.exceptions import CloseSpider
from ..items import FacebookSpiderItem
from scrapy.utils.response import open_in_browser


class FacebookSpider(scrapy.Spider):
    name = 'facebook'
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/76.0.3809.87 Safari/537.36"
    )
    cookie = 'locale=uk_UA;'
    default_headers = {
        'User-Agent': user_agent,
        'Accept-Language': 'uk-UA,ua;q=0.5',
        'cookie': cookie,
    }
    count_request_max = 0
    count_request = 0


    def __init__(self, *args, **kwargs):
        self.comment = []
        self.current_url = ''
        logger = logging.getLogger('scrapy.middleware')
        logger.setLevel(logging.WARNING)

        super(FacebookSpider, self).__init__(*args, **kwargs)
        if 'find' in kwargs:
            self.find = kwargs.get("find")

        if 'email' in kwargs:
            self.email = kwargs.get("email")

        if 'pass' in kwargs:
            self.password = kwargs.get("pass")

        if 'search_id' in kwargs:
            self.search_id = kwargs.get("search_id")

        if 'count' in kwargs:
            self.count_request_max = int(kwargs.get("count"))
        else:
            self.count_request_max = int(0)

        self.start_urls = ['https://mbasic.facebook.com']

    def parse(self, response):

        return FormRequest.from_response(
            response,
            formxpath='//form[contains(@action, "login")]',
            formdata={'email': self.email, 'pass': self.password},
            callback=self.parse_home
        )

    def parse_home(self, response):
        # open_in_browser(response)
        '''
               This method has multiple purposes:
               1) Handle failed logins due to facebook 'save-device' redirection
               2) Set language interface, if not already provided
               3) Navigate to given page
               '''
        # handle 'save-device' redirection
        if response.xpath("//div/a[contains(@href,'save-device')]"):
            self.logger.info('Going through the "save-device" checkpoint')
            return FormRequest.from_response(
                response,
                formdata={'name_action_selected': 'dont_save'},
                callback=self.parse_home
            )

        # href = 'https://mbasic.facebook.com/search/top/?q=' + self.find + '&source=filter&isTrending=0'
        href = 'https://mbasic.facebook.com/search/top/?q=' + self.find
        # self.logger.info('Scraping facebook page {}'.format(href))
        return scrapy.Request(url=href, callback=self.parse_page, meta={'index': 1})

    def parse_page(self, response):
        # open_in_browser(response)
        all_post = response.css('article')

        for post in all_post:
            if post.xpath('footer/div/a/@href').extract():
                self.comment.append(post.xpath('footer/div/a/@href').get())

        if response.css('#see_more_pager a::attr(href)').get():
            href = response.css('#see_more_pager a::attr(href)').get()
            # self.logger.info('Scraping facebook page {}'.format(href))
            yield scrapy.Request(url=href, callback=self.parse_page,
                                  meta={'index': 1})

        for post in self.comment:
            href = 'https://mbasic.facebook.com/' + post
            yield scrapy.Request(url=href, callback=self.parse_comment,
                           meta={'index': 1})


    def parse_comment(self, response):
        items = FacebookSpiderItem()

        all_comment = response.xpath('/html/body/div/div/div[2]/div/div/div[2]/div/div[5]/div')
        # open_in_browser(response)
        # return 0
        for comment in all_comment:
            title = next(iter(comment.xpath('div/div/text()').extract()), None)
            print(self.count_request)
            if self.count_request_max == 0 | self.count_request_max >= self.count_request:
                if title:
                    self.count_request = self.count_request + 1
                    items['title'] = title
                    items['page'] = response.request.url
                    items['search_id'] = self.search_id
                    yield items
        if self.count_request_max == 0 | self.count_request_max >= self.count_request:
            if response.xpath('.//div[contains(@id,"see_next")]/a/@href'):
                href = 'https://mbasic.facebook.com/' + response.xpath('.//div[contains(@id,"see_next")]/a/@href').get()
                yield scrapy.Request(url=href, callback=self.parse_comment,
                                     meta={'index': 1})