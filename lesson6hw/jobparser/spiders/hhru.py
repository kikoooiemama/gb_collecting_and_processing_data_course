import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    """
    Паук hh.ru
    """

    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = [
        'https://hh.ru/search/vacancy?clusters=true&area=2&enable_snippets=true&salary=&st=searchVacancy&text=python'
    ]

    # рекурсивная генератор-функция
    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@data-qa='pager-next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//a[@data-qa='vacancy-serp__vacancy-title']/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        # здесь обрабатывается страница с вакансией
        name = response.xpath("//h1//text()").get()
        salary = response.xpath('//span[@data-qa="vacancy-salary-compensation-type-net"]/text()').getall()
        url = response.url
        yield JobparserItem(name=name, salary=salary, url=url)
