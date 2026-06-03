import scrapy


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.books.toscrape.com"]
    start_urls = ["https://books.books.toscrape.com"]

    def parse(self, response):
        pass
