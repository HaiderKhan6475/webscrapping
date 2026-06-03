import scrapy


class BooksSpider(scrapy.Spider):
    # Spider ka naam 'books' rakha hai
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        # 1. Page par maujood saari 20 books ke blocks ko select kiya
        books = response.css("article.product_pod")

        # 2. Har book par loop chalaya
        for book in books:
            # Title extraction
            title = book.css("h3 a::text").get()

            # Availability extraction (Tutor Tip: getall() + join + strip use kiya)
            stock_text = book.css("p.instock.availability::text").getall()
            availability = "".join(stock_text).strip() if stock_text else None

            # Exact wahi output format jo task me pucha gaya tha
            yield {"title": title, "availability": availability}