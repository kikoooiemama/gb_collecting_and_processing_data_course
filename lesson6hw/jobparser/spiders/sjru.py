import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SjruSpider(scrapy.Spider):
    """
    Паук superjob.ru
    """
    name = 'sjru'
    allowed_domains = ['spb.superjob.ru']
    start_urls = ['https://spb.superjob.ru/vacancy/search/?keywords=Python']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//a[contains (@class, "f-test-link-Dalshe")]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath('//a[contains (@class,"icMQ_ _6AfZ9")]/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        # здесь обрабатывается страница с вакансией
        name = response.xpath('//h1/text()').get()
        salary = response.xpath('//span[@class="_1OuF_ ZON4b"]//text()').getall()
        url = response.url
        yield JobparserItem(name=name, salary=salary, url=url)
