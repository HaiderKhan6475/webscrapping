import scrapy
# Sahi item ko import karein aapke project name ke mutabik
from item_pipeline.items import ItemPipelineItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        books = response.css("article.product_pod")

        for book in books:
            # Sahi structural item yahan call hoga
            book_item = ItemPipelineItem()

            book_item["title"] = book.css("h3 a::text").get()
            book_item["price"] = book.css(".price_color::text").get()

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

            # Yeh item ab pipeline ke paas clean hone jayega
            yield book_item

        # Next page logic
        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)