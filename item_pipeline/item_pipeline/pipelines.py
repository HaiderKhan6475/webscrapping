class BookscraperPipeline:

    def process_item(self, item, spider):

        # 🌟 Price ka symbol '£' remove karne ka asli logic yahan hai!
        price_str = item.get("price")
        if price_str:
            clean_price = price_str.replace("£", "")
            item["price"] = float(clean_price)  # Number bana diya bina symbol ke

        # Extra cleaning (Optional par behtar data ke liye)
        rating_str = item.get("rating")
        if rating_str:
            item["rating"] = rating_str.lower()

        avail_str = item.get("availability")
        if avail_str:
            item["availability"] = avail_str.strip()

        return item


import os
import sqlite3


class SQLitePipeline:

    def __init__(self):
        # Sahi folder ka absolute path nikalne ke liye
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "books_data.db")

        self.con = sqlite3.connect(db_path)
        self.cur = self.con.cursor()

    def open_spider(self, spider):
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS books(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                price REAL,
                rating TEXT,
                availability TEXT,
                image_url TEXT
            )
        """
        )
        self.con.commit()

    def process_item(self, item, spider):
        self.cur.execute(
            """
            INSERT INTO books (title, price, rating, availability, image_url)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                item.get("title"),
                item.get("price"),
                item.get("rating"),
                item.get("availability"),
                item.get("image_url"),
            ),
        )
        self.con.commit()
        return item

    def close_spider(self, spider):
        self.con.close()