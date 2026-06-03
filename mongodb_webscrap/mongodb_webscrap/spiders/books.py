import scrapy
from mongodb_webscrap.items import MongodbWebscrapItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        books = response.css("article.product_pod")

        for book in books:
            book_item = MongodbWebscrapItem()

            book_item["title"] = book.css("h3 a::text").get()
            book_item["price"] = book.css(".price_color::text").get()

            # Image URL ko absolute rasta denge
            relative_url = book.css("img.thumbnail::attr(src)").get()
            book_item["image_url"] = response.urljoin(relative_url)

            rating_classes = book.css("p.star-rating::attr(class)").get()
            book_item["rating"] = (
                rating_classes.replace("star-rating", "").strip()
                if rating_classes
                else None
            )

            stock_text = book.css("p.instock.availability::text").getall()
            book_item["availability"] = (
                "".join(stock_text).strip() if stock_text else None
            )

            # Yeh item data cleaning aur MongoDB pipeline me jayega
            yield book_item

        # Next page ki pagination
        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)