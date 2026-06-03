import scrapy


class MongodbWebscrapItem(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field()
    rating = scrapy.Field()
    availability = scrapy.Field()
    image_url = scrapy.Field()