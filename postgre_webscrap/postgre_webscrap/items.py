import scrapy


class PostgresWebscrapItem(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field()
    rating = scrapy.Field()
    availability = scrapy.Field()
    image_url = scrapy.Field()