import pymongo


# =====================================================================
# 1. PIPELINE: Data Cleaning (Price, Rating, Availability)
# =====================================================================
class BookscraperPipeline:

    def process_item(self, item, spider):

        # Price se '£' symbol hatane aur use number (float) banane ka logic
        price_str = item.get("price")
        if price_str:
            clean_price = price_str.replace("£", "")
            item["price"] = float(clean_price)

        # Rating ko lowercase (chote letters) me convert karne ke liye
        rating_str = item.get("rating")
        if rating_str:
            item["rating"] = rating_str.lower()

        # Availability ke extra spaces saaf karne ke liye
        avail_str = item.get("availability")
        if avail_str:
            item["availability"] = avail_str.strip()

        # Cleaned item agli pipeline (MongoDB) ko pass hoga
        return item


# =====================================================================
# 2. PIPELINE: MongoDB Storage (Direct Database Insertion)
# =====================================================================
class MongoDBPipeline:

    def __init__(self):
        # Local MongoDB server se connect karein (Default port: 27017)
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        # Database ka naam 'mongodb_books_db' rakhenge
        self.db = self.client["mongodb_books_db"]
        # Collection (Table) ka naam 'scraped_books' rakhenge
        self.collection = self.db["scraped_books"]

    def process_item(self, item, spider):
        # Data ko dictionary me convert karke MongoDB me insert karenge
        self.collection.insert_one(dict(item))
        return item