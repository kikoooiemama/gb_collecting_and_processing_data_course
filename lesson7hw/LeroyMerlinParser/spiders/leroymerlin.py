import scrapy
from LeroyMerlinParser.items import LeroymerlinparserItem
from scrapy.loader import ItemLoader
from scrapy.http import HtmlResponse


class LeroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search):
        super().__init__()
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}']
        self.search_name = search

    def parse(self, response: HtmlResponse):
        next_page_link = response.xpath('//a[contains(@aria-label, "Следующая страница")]/@href').get()
        goods = response.xpath("//a[@data-qa='product-name']")
        for good in goods:
            yield response.follow(good, callback=self.parse_goods_page)

        # next_page_link = None

        if next_page_link:
            yield response.follow(next_page_link, callback=self.parse)

    def parse_goods_page(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroymerlinparserItem(), response=response)
        loader.add_xpath('name', '//h1/text()')
        loader.add_value('link', response.url)
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath('props', '//section[@id="nav-characteristics"]')
        loader.add_xpath('photos',
                         '//picture[@slot="pictures"]/source[@media=" only screen and (min-width: 1024px)"]/@data-origin')
        yield loader.load_item()
