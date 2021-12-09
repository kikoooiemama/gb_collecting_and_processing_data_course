from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from jobparser import settings
from jobparser.spiders.hhru import HhruSpider
from jobparser.spiders.sjru import SjruSpider

if __name__ == '__main__':
    # создаем объект с настройками
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    # создаем процесс, указываем настройки
    process = CrawlerProcess(settings=crawler_settings)

    # задаем паука hhru и sjru
    process.crawl(HhruSpider)
    process.crawl(SjruSpider)

    # запуск
    process.start()
