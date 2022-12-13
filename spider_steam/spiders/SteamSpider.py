import scrapy
from urllib.parse import urlencode
from urllib.parse import urlparse
from urllib.parse import urljoin
import re
import json
from spider_steam.items import SpiderSteamItem

queries = ['indie', 'strategy', 'minecraft']
API = '68e5a7021ef1ff81afcc17437031ff1e'

# Настроил Scraper API, но в итоге проблема была с ценой, почему-то он выкидывал ее в разных валютах)
def get_url(url):
    return url
    payload = {'api_key': API, 'url': url}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url

class SteamspiderSpider(scrapy.Spider):
    name = 'SteamSpider'
    allowed_domains = ['store.steampowered.com', 'api.scraperapi.com']
    start_urls = ['http://store.steampowered.com/']
    current_page = 1
    current_url = ''

    def start_requests(self):
        for query in queries:
            self.current_page = 1
            self.current_url = 'https://store.steampowered.com/search/?' + urlencode({'term': query, 'page': str(self.current_page)})
            yield scrapy.Request(url=get_url(self.current_url), callback=self.parse_keyword_response)


    def parse_keyword_response(self, response):
        print('parsing page', response.url)
        # Parsing this page
        games_urls = set()
        for res in response.xpath('//div[contains(@id, "search_result_container")]//a/@href'):
            if 'app' in res.get():
                games_urls.add(res.get()) # Add string to set

        for game_url in games_urls:
            yield scrapy.Request(url=get_url(game_url), callback=self.parse_game)

        # Starting with next page
        if self.current_page <= 1:
            self.current_page += 1
            self.current_url = self.current_url[:-1] + str(self.current_page)
            yield scrapy.Request(url=get_url(self.current_url), callback=self.parse_keyword_response) # Call the same function for the next page


    def parse_game(self, response):
        item = SpiderSteamItem()
        item['name'] = response.xpath('//div[contains(@class, "apphub_AppName")]/text()').get()
        item['category'] = response.xpath('//div[contains(@class, "blockbg")]//a/text()').getall()[1:]
        item['review_cnt'] = response.xpath('//meta[contains(@itemprop, "reviewCount")]/@content').get()
        item['score'] = response.xpath('//meta[contains(@itemprop, "ratingValue")]/@content').get()
        item['release_date'] = response.xpath('//div[contains(@class, "release_date")]//div[contains(@class, "date")]/text()').get()
        item['developer'] = response.xpath('//div[contains(@class, "dev_row")]//div[contains(@class, "summary column")]//a/text()').get()
        item['tags'] = response.xpath('//div[contains(@class, "glance_tags popular_tags")]//*/text()').getall()
        item['tags'] = [i.strip() for i in item['tags']][:-1]

        item['price'] = response.xpath('//div[contains(@class, "game_area_purchase_game")]//div[contains(@class, "game_purchase_price price")]/text()').get().strip()[:-5]

        if len(item['price']) == 0:
            item['price'] = 'Undefined'
        
        item['platforms'] = response.xpath('//div[contains(@class, "game_area_purchase_game_wrapper")]//div[contains(@class, "game_area_purchase_platform")]//*/@class').getall()
        item['platforms'] = [i[13:] for i in item['platforms']]
        item['platforms'] = list(set(item['platforms']))
        yield item